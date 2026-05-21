"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...core.universal_models import TransactionEdge as BankTransaction


class AlertEvent(BaseModel):
    """Alert event from ML worker or PaySim streamer."""
    model_config = ConfigDict(extra="forbid")
    
    txId: str
    risk_score: float
    aml_label: Optional[str] = None
    pattern: str
    timestamp: str
    amount: Optional[float] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    source: Optional[str] = None


class GraphNode(BaseModel):
    """Transaction node in the graph."""
    model_config = ConfigDict(extra="forbid")
    
    txId: str
    aml_label: str
    risk_score: float
    time_step: Optional[int] = None
    amount: Optional[float] = None
    pattern: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class GraphEdge(BaseModel):
    """Edge representing SENT_TO relationship."""
    model_config = ConfigDict(extra="forbid")
    
    source: str
    target: str
    is_suspicious: bool = False
    pattern: Optional[str] = None


class GraphResponse(BaseModel):
    """Graph data with nodes and edges."""
    model_config = ConfigDict(extra="forbid")
    
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class EvidencePackage(BaseModel):
    """Evidence package for a transaction chain."""
    model_config = ConfigDict(extra="forbid")
    
    txId: str
    chain: List[str]
    risk_scores: List[float]
    patterns: List[str]
    total_amount: float
    generated_at: datetime
    narrative: str


class GraphStats(BaseModel):
    """Graph statistics."""
    model_config = ConfigDict(extra="forbid")
    
    total_nodes: int
    fraud_nodes: int
    legit_nodes: int
    unknown_nodes: int
    total_edges: int


class IngestBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transactions: List[BankTransaction] = Field(default_factory=list)


class IngestBatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: int
    stored: int
    failed: int


class IngestStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    brokers: str | None = None
    topic: str | None = None
    group_id: str | None = None
    received: int
    stored: int
    failed: int
    last_error: str | None = None
    last_ingest_at: datetime | None = None
    last_tx_id: str | None = None
    last_batch_size: int
    kafka_connected: bool


class BankApiStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    base_url: str | None = None
    endpoint: str | None = None
    poll_interval_sec: int
    verify_ssl: bool
    received: int
    alerts_emitted: int
    failed: int
    last_error: str | None = None
    last_ingest_at: datetime | None = None
    last_tx_id: str | None = None
    last_batch_size: int
    last_pull_at: datetime | None = None
    running: bool


class BankApiFetchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    received: int
    alerts_emitted: int


class Entity360Response(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    kyc_risk_tier: int
    entity_type: str
    total_30d_volume: float
    peer_percentile: float
    historical_risk_scores: List[float]
    last_reviewed: Optional[datetime] = None


class CasePromoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_id: str
    reason: str


class CasePromoteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    status: str
    created_at: datetime
    cluster_id: str


class ModelStatus(BaseModel):
    """ML model status information."""
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
    
    last_trained: Optional[datetime] = None
    model_file_exists: bool
    total_scored: int


class SeedDemoResponse(BaseModel):
    """Response for seeding demo data."""
    model_config = ConfigDict(extra="forbid")

    seeded: bool
    nodes_created: int
    edges_created: int
    patterns: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    model_config = ConfigDict(extra="forbid")

    status: str
    service: Optional[str] = None


class StatusResponse(BaseModel):
    """Generic status response."""
    model_config = ConfigDict(extra="forbid")

    status: str


class FiuExportRequest(BaseModel):
    """FIU-IND export request."""
    model_config = ConfigDict(extra="forbid")

    cluster_id: str


# Legacy schemas for backward compatibility
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
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    timestamp: str
    alerts_sent: int
    model_version: str | None = None
    run_mode: str | None = None
