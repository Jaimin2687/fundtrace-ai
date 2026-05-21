"""
Entity 360 endpoints for account overview and risk context.
"""

import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ...core.security import verify_api_key
from ...core.auth import verify_investigator_access, AuthUser
from ...core.audit import audit_log
from .schemas import Entity360Response

router = APIRouter(prefix="/api/v1/entity", tags=["entity"])


@router.get(
    "/{account_id}/360",
    response_model=Entity360Response,
    dependencies=[Depends(verify_api_key)],
)
@audit_log(action_type="VIEW_ENTITY_360")
async def get_entity_360(
    account_id: str,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> Entity360Response:
    """
    Returns aggregated KYC and historical risk data for an account.
    Mock implementation for POC.
    """
    historical = [round(random.uniform(0.1, 0.95), 2) for _ in range(6)]
    return Entity360Response(
        account_id=account_id,
        kyc_risk_tier=random.randint(1, 5),
        entity_type=random.choice(["Retail", "Corporate", "Shell", "Unknown"]),
        total_30d_volume=round(random.uniform(1e5, 2e6), 2),
        peer_percentile=round(random.uniform(0.1, 0.99), 2),
        historical_risk_scores=historical,
        last_reviewed=datetime.now(timezone.utc),
    )
