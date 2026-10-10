"""Strict JSON schemas (hallucination-free)"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal
from enum import Enum

class HealthStatus(str, Enum):
    STABLE = "stable"
    DEGRADED = "degraded"
    STALE = "stale"
    ERROR = "error"

class CatalystActionType(str, Enum):
    RECOVER = "recover"
    PROPAGATE = "propagate"
    REBALANCE = "rebalance"
    ESCALATE = "escalate"

class CatalystActionStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"

class StateSnapshot(BaseModel):
    """Immutable state capture at T"""
    timestamp: int = Field(..., description="Unix milliseconds")
    seq: int = Field(..., description="Monotonic sequence number")
    state: Dict[str, Any] = Field(default_factory=dict)
    delta: Dict[str, Any] = Field(default_factory=dict)
    health: HealthStatus = HealthStatus.STABLE

class CatalystAction(BaseModel):
    """Deterministic action from DC catalyst"""
    id: str = Field(..., pattern="^[a-f0-9]{16}$")
    type: CatalystActionType
    timestamp: int
    source: Literal["DC", "AM", "MANUAL"]
    status: CatalystActionStatus
    result: Optional[Dict[str, Any]] = None

class KYCBinding(BaseModel):
    """CYU V3: Know Your Update compliance binding"""
    kyc_id: str = Field(..., description="Account identifier (hash)")
    validation_vector: str = Field(..., description="V3 validation hash")
    wire_route: str = Field(..., description="Transmission path")
    compliance_ts: int = Field(..., description="KYC validation timestamp")
    account_state: Literal["active", "pending", "restricted", "closed"]

class CYUTransmission(BaseModel):
    """CYU V3 wire transmission with variable validation"""
    tx_id: str = Field(..., pattern="^[a-f0-9]{16}$")
    kyc_binding: KYCBinding
    payload: Dict[str, Any]
    validation_vector_v3: str = Field(..., description="V3 variable validation")
    wire_signature: str = Field(..., description="Transmission signature")
    timestamp: int
    status: Literal["pending", "validated", "routed", "settled", "rejected"]

class RuntimeMetrics(BaseModel):
    """CLEAR audit metrics"""
    timestamp: int
    runtime_id: str
    events_captured: int
    actions_executed: int
    avg_latency_ms: float
    health: HealthStatus
