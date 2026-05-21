"""
Bank ingestion API for HTTP-based transaction ingestion.
Enabled only when KAFKA_ENABLED=true.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from ...core.auth import verify_investigator_access, AuthUser
from ...core.config import get_settings
from ...core.security import verify_api_key
from ...db.neo4j_client import get_driver
from ...services.ingest.bank_ingest import ingest_transactions, get_ingest_stats
from ...services.ingest.bank_api import fetch_and_process, get_bank_api_stats
from .schemas import (
    IngestBatchRequest,
    IngestBatchResponse,
    IngestStatus,
    BankApiStatus,
    BankApiFetchResponse,
)
from . import stream

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


def _ensure_enabled():
    settings = get_settings()
    if not settings.KAFKA_ENABLED:
        raise HTTPException(status_code=503, detail="Bank ingest is disabled")
    return settings


def _ensure_bank_api_enabled():
    settings = get_settings()
    if not settings.BANK_API_ENABLED:
        raise HTTPException(status_code=503, detail="Bank API ingest is disabled")
    return settings


@router.get("/status", response_model=IngestStatus, dependencies=[Depends(verify_api_key)])
async def get_ingest_status(
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> IngestStatus:
    settings = get_settings()
    stats = get_ingest_stats()
    return IngestStatus(
        enabled=settings.KAFKA_ENABLED,
        brokers=settings.KAFKA_BROKERS,
        topic=settings.KAFKA_TOPIC,
        group_id=settings.KAFKA_GROUP_ID,
        received=stats.received,
        stored=stats.stored,
        failed=stats.failed,
        last_error=stats.last_error,
        last_ingest_at=stats.last_ingest_at,
        last_tx_id=stats.last_tx_id,
        last_batch_size=stats.last_batch_size,
        kafka_connected=stats.kafka_connected,
    )


@router.post(
    "/transactions",
    response_model=IngestBatchResponse,
    dependencies=[Depends(verify_api_key)],
)
async def ingest_transactions_http(
    payload: IngestBatchRequest,
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> IngestBatchResponse:
    _ensure_enabled()
    driver = getattr(request.app.state, "neo4j_driver", None) or get_driver()
    result = ingest_transactions(driver, payload.transactions)
    return IngestBatchResponse(**result)


@router.get("/bank/status", response_model=BankApiStatus, dependencies=[Depends(verify_api_key)])
async def get_bank_status(
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> BankApiStatus:
    settings = get_settings()
    stats = await get_bank_api_stats()
    return BankApiStatus(
        enabled=settings.BANK_API_ENABLED,
        base_url=settings.BANK_API_BASE_URL,
        endpoint=settings.BANK_API_ENDPOINT,
        poll_interval_sec=settings.BANK_API_POLL_INTERVAL_SEC,
        verify_ssl=settings.BANK_API_VERIFY_SSL,
        received=stats.received,
        alerts_emitted=stats.alerts_emitted,
        failed=stats.failed,
        last_error=stats.last_error,
        last_ingest_at=stats.last_ingest_at,
        last_tx_id=stats.last_tx_id,
        last_batch_size=stats.last_batch_size,
        last_pull_at=stats.last_pull_at,
        running=stats.running,
    )


@router.post(
    "/bank/fetch",
    response_model=BankApiFetchResponse,
    dependencies=[Depends(verify_api_key)],
)
async def fetch_bank_batch(
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> BankApiFetchResponse:
    settings = _ensure_bank_api_enabled()
    result = await fetch_and_process(stream.alert_queue, settings)
    return BankApiFetchResponse(**result)
