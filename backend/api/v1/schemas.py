from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AccountNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    account_type: str
    kyc_risk_baseline: float
    total_volume: float
    aml_label: int | None = None


class TransactionEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tx_id: str
    source_id: str
    target_id: str
    amount: float
    timestamp: str
    is_structuring: bool


class GraphFocusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: List[AccountNode] = Field(default_factory=list)
    edges: List[TransactionEdge] = Field(default_factory=list)


class AlertPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str | None = None
    cluster_id: str
    risk_score: float
    threat_type: str
    narrative: str
    nodes: List[AccountNode] = Field(default_factory=list)
    edges: List[TransactionEdge] = Field(default_factory=list)


class ModelStatusPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    alerts_sent: int
    model_version: str | None = None
    run_mode: str | None = None
