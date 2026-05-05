import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Request, WebSocket
from starlette.websockets import WebSocketDisconnect

from ...core.config import get_settings
from .schemas import AccountNode, AlertPayload, ModelStatusPayload, TransactionEdge

router = APIRouter(prefix="/api/v1/stream", tags=["stream"])


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            connections = list(self._connections)

        for websocket in connections:
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                await self.disconnect(websocket)


manager = ConnectionManager()
_broadcaster_task: asyncio.Task | None = None
_alert_buffer: List[AlertPayload] = []
_model_status: ModelStatusPayload | None = None


def _store_alert(payload: AlertPayload, max_size: int = 50) -> None:
    _alert_buffer.append(payload)
    if len(_alert_buffer) > max_size:
        _alert_buffer[:] = _alert_buffer[-max_size:]


def _build_mock_alert() -> AlertPayload:
    now = datetime.now(timezone.utc)
    cluster_id = f"CL-{random.randint(1000, 9999)}"
    nodes = [
        AccountNode(
            account_id="ACC-0421",
            account_type="Retail",
            kyc_risk_baseline=0.18,
            total_volume=12540000.0,
        ),
        AccountNode(
            account_id="ACC-1733",
            account_type="Retail",
            kyc_risk_baseline=0.24,
            total_volume=8420000.0,
        ),
        AccountNode(
            account_id="ACC-2994",
            account_type="Corporate",
            kyc_risk_baseline=0.37,
            total_volume=21490000.0,
        ),
        AccountNode(
            account_id="ACC-3888",
            account_type="Shell",
            kyc_risk_baseline=0.82,
            total_volume=43750000.0,
        ),
    ]

    edges = [
        TransactionEdge(
            tx_id="TX-MOCK-0001",
            source_id="ACC-0421",
            target_id="ACC-3888",
            amount=195000.0,
            timestamp=(now - timedelta(hours=36)).isoformat(),
            is_structuring=True,
        ),
        TransactionEdge(
            tx_id="TX-MOCK-0002",
            source_id="ACC-1733",
            target_id="ACC-3888",
            amount=195000.0,
            timestamp=(now - timedelta(hours=30)).isoformat(),
            is_structuring=True,
        ),
        TransactionEdge(
            tx_id="TX-MOCK-0003",
            source_id="ACC-3888",
            target_id="ACC-2994",
            amount=2685000.0,
            timestamp=(now - timedelta(hours=4)).isoformat(),
            is_structuring=False,
        ),
    ]

    narrative = (
        "Account ACC-3888 received multiple INR 1.95L transfers within 72 hours "
        "and forwarded 87% to a corporate account after a 36-hour dwell time."
    )

    return AlertPayload(
        timestamp=now.isoformat(),
        cluster_id=cluster_id,
        risk_score=88.4,
        threat_type="Rapid Layering",
        narrative=narrative,
        nodes=nodes,
        edges=edges,
    )


def _store_model_status(payload: ModelStatusPayload) -> None:
    global _model_status
    _model_status = payload


async def _alert_broadcaster() -> None:
    while True:
        payload = _build_mock_alert()
        _store_alert(payload)
        await manager.broadcast(payload.model_dump_json())
        await asyncio.sleep(5)


def start_broadcaster() -> None:
    global _broadcaster_task
    if _broadcaster_task is None or _broadcaster_task.done():
        _broadcaster_task = asyncio.create_task(_alert_broadcaster())


def stop_broadcaster() -> None:
    if _broadcaster_task and not _broadcaster_task.done():
        _broadcaster_task.cancel()


@router.websocket("/alerts")
async def alerts_stream(websocket: WebSocket) -> None:
    settings = get_settings()
    api_key = (
        websocket.headers.get("x-api-key")
        or websocket.query_params.get("token")
        or websocket.query_params.get("api_key")
    )
    if api_key != settings.API_KEY:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        for payload in _alert_buffer:
            await websocket.send_text(payload.model_dump_json())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.post("/ingest")
async def ingest_alert(payload: AlertPayload, request: Request) -> dict:
    settings = get_settings()
    api_key = request.headers.get("x-api-key")
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    _store_alert(payload)
    await manager.broadcast(payload.model_dump_json())
    return {"status": "ok"}


@router.post("/status")
async def ingest_status(payload: ModelStatusPayload, request: Request) -> dict:
    settings = get_settings()
    api_key = request.headers.get("x-api-key")
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    _store_model_status(payload)
    return {"status": "ok"}


@router.get("/status/latest", response_model=ModelStatusPayload | None)
async def latest_status() -> ModelStatusPayload | None:
    return _model_status
