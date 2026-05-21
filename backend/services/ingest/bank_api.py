"""
Bank API ingestion that streams batches directly to the ML worker queue.
No Neo4j persistence.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ...core.config import Settings
from ...core.model_registry import get_model_info
from ...worker import ml_worker
from ...api.v1.evidence import pattern_from_score


class BankApiTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tx_id: str
    source_id: str
    target_id: str
    amount: float
    timestamp: datetime
    currency: str = "INR"
    type: str = "TRANSFER"
    step: Optional[int] = None
    oldbalanceOrg: float = 0.0
    newbalanceOrig: float = 0.0
    oldbalanceDest: float = 0.0
    newbalanceDest: float = 0.0
    isFlaggedFraud: bool = False
    features: Optional[dict] = None


@dataclass
class BankApiStats:
    received: int = 0
    alerts_emitted: int = 0
    failed: int = 0
    last_error: Optional[str] = None
    last_ingest_at: Optional[datetime] = None
    last_tx_id: Optional[str] = None
    last_batch_size: int = 0
    last_pull_at: Optional[datetime] = None
    running: bool = False


_stats = BankApiStats()
_stats_lock = asyncio.Lock()


async def _update_stats(**kwargs) -> None:
    async with _stats_lock:
        for key, value in kwargs.items():
            setattr(_stats, key, value)


async def get_bank_api_stats() -> BankApiStats:
    async with _stats_lock:
        return BankApiStats(**asdict(_stats))


def _paysim_props(tx: BankApiTransaction) -> dict:
    step_value = tx.step if tx.step is not None else int(tx.timestamp.timestamp())
    return {
        "step": step_value,
        "amount": float(tx.amount),
        "oldbalanceOrg": float(tx.oldbalanceOrg),
        "newbalanceOrig": float(tx.newbalanceOrig),
        "oldbalanceDest": float(tx.oldbalanceDest),
        "newbalanceDest": float(tx.newbalanceDest),
        "isFlaggedFraud": 1.0 if tx.isFlaggedFraud else 0.0,
        "type": tx.type,
    }


def _elliptic_features(tx: BankApiTransaction) -> dict:
    if not isinstance(tx.features, dict):
        return {}
    return {f"f{i}": float(tx.features.get(f"f{i}", 0.0)) for i in range(1, 166)}


def _score_transaction(tx: BankApiTransaction) -> float:
    model_info = get_model_info()
    if model_info.source == "paysim":
        model = ml_worker._load_paysim_model(model_info.path)
        features = ml_worker._build_paysim_vector_from_props(_paysim_props(tx))
        return float(model.predict_proba(features.reshape(1, -1))[0, 1])
    if model_info.source == "elliptic":
        features = _elliptic_features(tx)
        if features:
            return ml_worker.score_transaction(features)
    return 0.0


async def _process_transactions(
    transactions: List[BankApiTransaction], alert_queue: asyncio.Queue
) -> dict:
    alerts_emitted = 0
    for tx in transactions:
        try:
            risk_score = _score_transaction(tx)
            pattern = pattern_from_score(risk_score)
            aml_label = "fraud" if risk_score >= 0.75 else "legit"
            alert = {
                "txId": tx.tx_id,
                "risk_score": round(risk_score, 4),
                "aml_label": aml_label,
                "pattern": pattern,
                "timestamp": tx.timestamp.astimezone(timezone.utc).isoformat(),
                "amount": float(tx.amount),
                "from_account": tx.source_id,
                "to_account": tx.target_id,
                "source": "bank_api",
            }
            await alert_queue.put(alert)
            alerts_emitted += 1
        except Exception as exc:
            stats = await get_bank_api_stats()
            await _update_stats(
                failed=stats.failed + 1,
                last_error=str(exc),
                last_ingest_at=datetime.now(timezone.utc),
                last_tx_id=tx.tx_id,
            )

    stats = await get_bank_api_stats()
    await _update_stats(
        received=stats.received + len(transactions),
        alerts_emitted=stats.alerts_emitted + alerts_emitted,
        last_error=None,
        last_ingest_at=datetime.now(timezone.utc),
        last_tx_id=transactions[-1].tx_id if transactions else None,
        last_batch_size=len(transactions),
    )
    return {"received": len(transactions), "alerts_emitted": alerts_emitted}


def _parse_payload(payload: object) -> List[BankApiTransaction]:
    if isinstance(payload, list):
        return [BankApiTransaction.model_validate(item) for item in payload]
    if isinstance(payload, dict):
        if "transactions" in payload and isinstance(payload["transactions"], list):
            return [BankApiTransaction.model_validate(item) for item in payload["transactions"]]
        return [BankApiTransaction.model_validate(payload)]
    raise ValueError("Unsupported bank API payload format")


async def fetch_bank_batch(settings: Settings) -> List[BankApiTransaction]:
    if not settings.BANK_API_BASE_URL:
        raise RuntimeError("BANK_API_BASE_URL is not configured")
    try:
        import httpx
    except ModuleNotFoundError as exc:
        raise RuntimeError("Bank API ingestion requires httpx") from exc
    endpoint = settings.BANK_API_ENDPOINT
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    url = settings.BANK_API_BASE_URL.rstrip("/") + endpoint
    headers = {}
    if settings.BANK_API_AUTH_TOKEN:
        headers[settings.BANK_API_AUTH_HEADER] = settings.BANK_API_AUTH_TOKEN
    timeout = httpx.Timeout(settings.BANK_API_TIMEOUT_SEC)
    async with httpx.AsyncClient(verify=settings.BANK_API_VERIFY_SSL, timeout=timeout) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
    return _parse_payload(payload)


async def fetch_and_process(alert_queue: asyncio.Queue, settings: Settings) -> dict:
    await _update_stats(last_pull_at=datetime.now(timezone.utc))
    transactions = await fetch_bank_batch(settings)
    return await _process_transactions(transactions, alert_queue)


async def run_bank_api_poller(alert_queue: asyncio.Queue, settings: Settings) -> None:
    await _update_stats(running=True)
    try:
        while True:
            await fetch_and_process(alert_queue, settings)
            await asyncio.sleep(settings.BANK_API_POLL_INTERVAL_SEC)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        stats = await get_bank_api_stats()
        await _update_stats(
            failed=stats.failed + 1,
            last_error=str(exc),
            last_ingest_at=datetime.now(timezone.utc),
        )
    finally:
        await _update_stats(running=False)
