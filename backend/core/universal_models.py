"""
Universal data models shared across FundTrace microservices.
These act as the source of truth for validation across services.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class AccountNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(..., description="Unique CBS Account Identifier")
    entity_type: str = Field(..., pattern="^(Retail|Corporate|Shell|Unknown)$")
    kyc_risk_tier: int = Field(..., ge=1, le=5)
    total_30d_volume: float = Field(default=0.0)
    created_at: datetime


class TransactionEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tx_id: str = Field(..., description="Unique Transaction ID")
    source_id: str
    target_id: str
    amount: float = Field(..., gt=0.0)
    currency: str = Field(default="INR")
    timestamp: datetime
    is_structuring_flag: bool = Field(default=False)


class ExplainableNarrative(BaseModel):
    model_config = ConfigDict(extra="forbid")

    threat_type: str = Field(..., pattern="^(Round-Tripping|Rapid Layering|Smurfing)$")
    risk_score: float = Field(..., ge=0, le=100)
    feature_contributions: Dict[str, float] = Field(
        ..., description="XGBoost SHAP values"
    )
    human_readable_text: str = Field(..., max_length=1000)


class AlertPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_id: str
    narrative: ExplainableNarrative
    nodes: List[AccountNode]
    edges: List[TransactionEdge]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
