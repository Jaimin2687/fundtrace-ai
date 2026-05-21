"""
Case management endpoints for promoting alerts to investigations.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ...core.security import verify_api_key
from ...core.auth import verify_investigator_access, AuthUser
from ...core.audit import audit_log
from .schemas import CasePromoteRequest, CasePromoteResponse

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


@router.post(
    "/promote",
    response_model=CasePromoteResponse,
    dependencies=[Depends(verify_api_key)],
)
@audit_log(action_type="PROMOTE_CASE")
async def promote_case(
    payload: CasePromoteRequest,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> CasePromoteResponse:
    """
    Converts an alert into a formal investigation case.
    """
    case_id = f"CASE-{uuid.uuid4().hex[:10].upper()}"
    return CasePromoteResponse(
        case_id=case_id,
        status="created",
        created_at=datetime.now(timezone.utc),
        cluster_id=payload.cluster_id,
    )
