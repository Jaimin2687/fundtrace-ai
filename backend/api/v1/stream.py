"""
Streaming API endpoints for real-time alerts and model status.
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ...core.security import verify_api_key
from ...core.model_registry import get_model_info
from ...db.neo4j_client import get_driver
from .schemas import AlertEvent, ModelStatus

router = APIRouter(prefix="/api/v1/stream", tags=["stream"])

# Global alert queue shared with ML worker
alert_queue: asyncio.Queue = asyncio.Queue()

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for alert streaming."""
    
    def __init__(self) -> None:
        self._connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Add a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all connected clients."""
        async with self._lock:
            connections = list(self._connections)

        for websocket in connections:
            try:
                await websocket.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                await self.disconnect(websocket)


manager = ConnectionManager()


async def alert_broadcaster():
    """
    Background task that reads from alert_queue and broadcasts to WebSocket clients.
    """
    print("[Alert Broadcaster] Started")
    
    while True:
        try:
            alert = await alert_queue.get()
            
            try:
                payload = AlertEvent.model_validate(alert)
            except Exception as exc:
                print(f"[Alert Broadcaster] Invalid alert payload: {exc}")
                continue

            message = payload.model_dump_json()
            await manager.broadcast(message)
            print(f"[Alert Broadcaster] Broadcasted alert: {payload.txId}")
            
        except Exception as e:
            print(f"[Alert Broadcaster] Error: {str(e)}")
            await asyncio.sleep(1)




@router.websocket("/alerts")
async def alerts_websocket(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time alert streaming.
    Clients connect and receive alerts as they are generated.
    """
    await manager.connect(websocket)
    print(f"[WebSocket] Client connected. Total connections: {len(manager._connections)}")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print(f"[WebSocket] Client disconnected. Total connections: {len(manager._connections)}")


@router.websocket("/threats")
async def threats_websocket(websocket: WebSocket) -> None:
    """
    Architecture-spec WebSocket endpoint for critical alerts.
    Mirrors /alerts for live data.
    """
    await manager.connect(websocket)
    print(f"[WebSocket] Threat client connected. Total connections: {len(manager._connections)}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print(f"[WebSocket] Threat client disconnected. Total connections: {len(manager._connections)}")


@router.get("/model-status", response_model=ModelStatus, dependencies=[Depends(verify_api_key)])
async def get_model_status() -> ModelStatus:
    """Get ML model status information."""
    model_info = get_model_info()
    model_path = model_info.path
    
    model_file_exists = os.path.exists(model_path)
    
    last_trained = None
    if model_file_exists:
        mtime = os.path.getmtime(model_path)
        last_trained = datetime.fromtimestamp(mtime, tz=timezone.utc)
    
    total_scored = 0
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (t:Transaction)
                WHERE coalesce(t.risk_score, 0) > 0
                RETURN count(t) AS total_scored
                """
            ).single()
            total_scored = int(result["total_scored"] or 0) if result else 0
    except Exception as exc:
        print(f"[Model Status] Error querying Neo4j: {exc}")
    
    return ModelStatus(
        last_trained=last_trained,
        model_file_exists=model_file_exists,
        total_scored=total_scored,
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check for streaming service."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_connections": len(manager._connections),
    }
