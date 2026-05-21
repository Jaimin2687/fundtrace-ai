"""
Kafka + HTTP ingestion for real bank transactions.
Enabled only when KAFKA_ENABLED=true.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable, List, Optional

from neo4j import Driver

from ...core.config import Settings
from ...core.universal_models import TransactionEdge


@dataclass
class IngestStats:
    received: int = 0
    stored: int = 0
    failed: int = 0
    last_error: Optional[str] = None
    last_ingest_at: Optional[datetime] = None
    last_tx_id: Optional[str] = None
    last_batch_size: int = 0
    kafka_connected: bool = False


_stats = IngestStats()
_stats_lock = threading.Lock()
_stop_event: Optional[threading.Event] = None
_consumer_thread: Optional[threading.Thread] = None


def _update_stats(**kwargs) -> None:
    with _stats_lock:
        for key, value in kwargs.items():
            setattr(_stats, key, value)


def get_ingest_stats() -> IngestStats:
    with _stats_lock:
        return IngestStats(**asdict(_stats))


def _coerce_timestamp(value: datetime) -> tuple[str, int]:
    if isinstance(value, datetime):
        ts = value.astimezone(timezone.utc)
    else:
        raise ValueError("timestamp must be a datetime")
    return ts.isoformat(), int(ts.timestamp())


def ingest_transactions(driver: Driver, transactions: Iterable[TransactionEdge]) -> dict:
    batch: List[dict] = []
    last_tx_id = None
    for tx in transactions:
        ts_iso, time_step = _coerce_timestamp(tx.timestamp)
        batch.append(
            {
                "txId": tx.tx_id,
                "amount": float(tx.amount),
                "currency": tx.currency,
                "time_step": time_step,
                "timestamp": ts_iso,
                "nameOrig": tx.source_id,
                "nameDest": tx.target_id,
                "tx_type": "TRANSFER",
            }
        )
        last_tx_id = tx.tx_id

    if not batch:
        return {"accepted": 0, "stored": 0, "failed": 0}

    query = """
    UNWIND $batch AS tx
    MERGE (t:Transaction {txId: tx.txId})
    SET t.amount = tx.amount,
        t.currency = tx.currency,
        t.time_step = tx.time_step,
        t.timestamp = tx.timestamp,
        t.nameOrig = tx.nameOrig,
        t.nameDest = tx.nameDest,
        t.tx_type = tx.tx_type,
        t.aml_label = coalesce(t.aml_label, "unknown"),
        t.risk_score = coalesce(t.risk_score, 0.0)
    WITH t, tx
    CALL {
        WITH tx
        OPTIONAL MATCH (prev_origin:Transaction)
        WHERE (prev_origin.nameOrig = tx.nameOrig OR prev_origin.nameDest = tx.nameOrig)
          AND prev_origin.time_step < tx.time_step
        RETURN prev_origin
        ORDER BY prev_origin.time_step DESC
        LIMIT 1
    }
    WITH t, tx, prev_origin
    FOREACH (_ IN CASE WHEN prev_origin IS NULL THEN [] ELSE [1] END |
        MERGE (prev_origin)-[:TRANSFERRED_TO]->(t)
    )
    CALL {
        WITH tx
        OPTIONAL MATCH (prev_dest:Transaction)
        WHERE (prev_dest.nameOrig = tx.nameDest OR prev_dest.nameDest = tx.nameDest)
          AND prev_dest.time_step < tx.time_step
        RETURN prev_dest
        ORDER BY prev_dest.time_step DESC
        LIMIT 1
    }
    WITH t, tx, prev_dest
    FOREACH (_ IN CASE WHEN prev_dest IS NULL THEN [] ELSE [1] END |
        MERGE (prev_dest)-[:TRANSFERRED_TO]->(t)
    )
    RETURN count(t) AS stored
    """

    stored = 0
    try:
        with driver.session() as session:
            result = session.run(query, batch=batch).single()
            stored = int(result["stored"] or 0) if result else 0
    except Exception as exc:
        current = get_ingest_stats()
        _update_stats(
            failed=current.failed + len(batch),
            last_error=str(exc),
            last_ingest_at=datetime.now(timezone.utc),
            last_tx_id=last_tx_id,
            last_batch_size=len(batch),
        )
        raise

    current = get_ingest_stats()
    _update_stats(
        received=current.received + len(batch),
        stored=current.stored + stored,
        last_error=None,
        last_ingest_at=datetime.now(timezone.utc),
        last_tx_id=last_tx_id,
        last_batch_size=len(batch),
    )
    return {"accepted": len(batch), "stored": stored, "failed": len(batch) - stored}


def _parse_payload(payload: object) -> list[TransactionEdge]:
    if isinstance(payload, list):
        return [TransactionEdge.model_validate(item) for item in payload]
    if isinstance(payload, dict):
        if "transactions" in payload and isinstance(payload["transactions"], list):
            return [TransactionEdge.model_validate(item) for item in payload["transactions"]]
        return [TransactionEdge.model_validate(payload)]
    raise ValueError("Unsupported payload format")


def start_kafka_consumer(driver: Driver, settings: Settings) -> None:
    global _stop_event, _consumer_thread
    if _consumer_thread and _consumer_thread.is_alive():
        return
    if not settings.KAFKA_BROKERS or not settings.KAFKA_TOPIC:
        _update_stats(last_error="Kafka brokers/topic not configured")
        return
    try:
        from kafka import KafkaConsumer
    except ModuleNotFoundError as exc:
        _update_stats(last_error="kafka-python is not installed")
        raise RuntimeError("Kafka ingestion requires kafka-python") from exc
    _stop_event = threading.Event()

    def _run() -> None:
        brokers = [broker.strip() for broker in settings.KAFKA_BROKERS.split(",") if broker.strip()]
        consumer_kwargs = {
            "bootstrap_servers": brokers,
            "group_id": settings.KAFKA_GROUP_ID,
            "auto_offset_reset": "latest",
            "enable_auto_commit": True,
        }
        if settings.KAFKA_SECURITY_PROTOCOL:
            consumer_kwargs["security_protocol"] = settings.KAFKA_SECURITY_PROTOCOL
        if settings.KAFKA_SASL_MECHANISM:
            consumer_kwargs["sasl_mechanism"] = settings.KAFKA_SASL_MECHANISM
        if settings.KAFKA_USERNAME:
            consumer_kwargs["sasl_plain_username"] = settings.KAFKA_USERNAME
        if settings.KAFKA_PASSWORD:
            consumer_kwargs["sasl_plain_password"] = settings.KAFKA_PASSWORD

        consumer = KafkaConsumer(settings.KAFKA_TOPIC, **consumer_kwargs)
        _update_stats(kafka_connected=True)
        try:
            while not _stop_event.is_set():
                records = consumer.poll(timeout_ms=settings.KAFKA_POLL_TIMEOUT_MS, max_records=settings.KAFKA_BATCH_SIZE)
                if not records:
                    continue
                batch_items: List[TransactionEdge] = []
                for partition_records in records.values():
                    for record in partition_records:
                        try:
                            payload = json.loads(record.value.decode("utf-8"))
                            batch_items.extend(_parse_payload(payload))
                        except Exception as exc:
                            current = get_ingest_stats()
                            _update_stats(
                                failed=current.failed + 1,
                                last_error=f"Kafka parse error: {exc}",
                                last_ingest_at=datetime.now(timezone.utc),
                                last_batch_size=0,
                            )
                if batch_items:
                    ingest_transactions(driver, batch_items)
        finally:
            consumer.close()
            _update_stats(kafka_connected=False)

    _consumer_thread = threading.Thread(target=_run, daemon=True)
    _consumer_thread.start()


def stop_kafka_consumer() -> None:
    if _stop_event:
        _stop_event.set()
    if _consumer_thread and _consumer_thread.is_alive():
        _consumer_thread.join(timeout=5)
