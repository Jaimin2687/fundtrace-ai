"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertEvent(BaseModel):
    """Alert event from ML worker or PaySim streamer."""
    model_config = ConfigDict(extra="forbid")
    
    txId: str
    risk_score: float
    aml_label: Optional[str] = None
    pattern: str
    timestamp: str
    amount: Optional[float] = None
    source: Optional[str] = None


class GraphNode(BaseModel):
    """Transaction node in the graph."""
    model_config = ConfigDict(extra="forbid")
    
    txId: str
    aml_label: str
    risk_score: float
    x: Optional[float] = None
    y: Optional[float] = None


class GraphEdge(BaseModel):
    """Edge representing SENT_TO relationship."""
    model_config = ConfigDict(extra="forbid")
    
    source: str
    target: str


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


class ModelStatus(BaseModel):
    """ML model status information."""
    model_config = ConfigDict(extra="forbid")
    
    last_trained: Optional[datetime] = None
    model_file_exists: bool
    total_scored: int


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
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    alerts_sent: int
    model_version: str | None = None
    run_mode: str | None = None
