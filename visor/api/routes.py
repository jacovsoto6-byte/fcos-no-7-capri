"""FastAPI routes for Caprise Visor REST control plane"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import time
from datetime import datetime

from ..core.caprise import Caprise
from ..core.am_manager import AMProvider
from ..core.dc_catalyst import DCProvider
from ..core.cyu_validator import CYUValidator
from ..core.shine_buff import ShineBuff
from ..core.schemas import HealthStatus

app = FastAPI(
    title="Caprise Visor",
    version="1.0.0",
    description="Multi-runtime CLEAR/PACE orchestrator with CYU KYC compliance"
)

# Global instances
AM = AMProvider(refresh_hz=10.0, stale_after_ms=500)
DC = DCProvider()
CAPRISE = Caprise(AM, DC)
CYU_VALIDATOR = CYUValidator(secret_key="visor-secret-key-v1")

# Request models
class StateRefreshRequest(BaseModel):
    state: Dict[str, Any]

class ActionExecuteRequest(BaseModel):
    type: str
    params: Optional[Dict[str, Any]] = None

class RuntimeRegisterRequest(BaseModel):
    name: str
    version: str
    language: str
    capabilities: list
    refresh_hz: float = 10.0

class KYCRegisterRequest(BaseModel):
    kyc_id: str
    wire_route: str
    account_state: str = "pending"

class CYUTransmitRequest(BaseModel):
    kyc_id: str
    payload: Dict[str, Any]

# State
registered_runtimes = {}  # runtime_id -> metadata

# Routes: State & Health
@app.get("/visor/state")
def get_state():
    """Get current system state snapshot"""
    return CAPRISE.get_state()

@app.get("/visor/health")
def get_health():
    """Get AM/DC health and system latency"""
    return {
        "timestamp": int(time.time() * 1000),
        "am_health": AM.get_health(),
        "dc_health": DC.get_metrics(),
        "caprise_running": CAPRISE.running
    }

@app.post("/visor/state/refresh")
def refresh_state(req: StateRefreshRequest):
    """Trigger AM refresh cycle immediately"""
    polished = ShineBuff.polish_state(req.state)
    action = CAPRISE.refresh_cycle(polished)
    return {
        "state": CAPRISE.get_state(),
        "action": action.dict() if action else None
    }

# Routes: Metrics & Audit
@app.get("/visor/metrics")
def get_metrics():
    """Get CLEAR audit log and metrics"""
    return {
        "timestamp": int(time.time() * 1000),
        "caprise_metrics": CAPRISE.get_metrics(),
        "dc_capture_log": [
            s.dict() for s in DC.capture_log[-10:]  # Last 10 captures
        ]
    }

@app.get("/visor/metrics/delta")
def get_delta_metrics():
    """Get DC delta capture history"""
    return {
        "timestamp": int(time.time() * 1000),
        "deltas": [
            {"seq": s.seq, "delta": s.delta, "health": s.health}
            for s in DC.capture_log[-20:]  # Last 20
        ]
    }

@app.get("/visor/metrics/catalyst")
def get_catalyst_metrics():
    """Get catalyst action history"""
    return {
        "timestamp": int(time.time() * 1000),
        "actions": [
            a.dict() for a in DC.action_history[-20:]  # Last 20
        ]
    }

# Routes: Control
@app.post("/visor/action")
def execute_action(req: ActionExecuteRequest):
    """Execute a catalyst action manually"""
    # Handler would be registered in CAPRISE
    return {
        "status": "queued",
        "action_type": req.type,
        "timestamp": int(time.time() * 1000)
    }

@app.post("/visor/runtime/pause")
def pause_runtime():
    """Pause PACE event loop"""
    CAPRISE.stop()
    return {"status": "paused", "running": CAPRISE.running}

@app.post("/visor/runtime/resume")
def resume_runtime(bg_tasks: BackgroundTasks):
    """Resume PACE event loop"""
    def dummy_state_provider():
        return CAPRISE.get_state()
    
    bg_tasks.add_task(CAPRISE.run_loop, dummy_state_provider, 0.1)
    return {"status": "resumed", "running": CAPRISE.running}

@app.get("/visor/runtime/config")
def get_runtime_config():
    """Get runtime configuration"""
    return {
        "refresh_hz": AM.refresh_hz,
        "stale_after_ms": AM.stale_after_ms,
        "running": CAPRISE.running
    }

# Routes: Multi-Runtime Coordination
@app.get("/visor/runtimes")
def list_runtimes():
    """List registered runtime clients"""
    return {
        "timestamp": int(time.time() * 1000),
        "runtimes": list(registered_runtimes.values())
    }

@app.post("/visor/runtimes/register")
def register_runtime(req: RuntimeRegisterRequest):
    """Register a new runtime client"""
    runtime_id = f"rt_{uuid.uuid4().hex[:16]}"
    
    registered_runtimes[runtime_id] = {
        "runtime_id": runtime_id,
        "name": req.name,
        "version": req.version,
        "language": req.language,
        "capabilities": req.capabilities,
        "refresh_hz": req.refresh_hz,
        "registered_at": int(time.time() * 1000)
    }
    
    return {
        "runtime_id": runtime_id,
        "visor_version": "1.0.0",
        "sync_interval_ms": 100,
        "ripz_port": 5555
    }

@app.post("/visor/runtimes/{runtime_id}/sync")
def sync_to_runtime(runtime_id: str):
    """Sync state to specific runtime"""
    if runtime_id not in registered_runtimes:
        raise HTTPException(status_code=404, detail="Runtime not found")
    
    return {
        "runtime_id": runtime_id,
        "state": CAPRISE.get_state(),
        "seq": CAPRISE.seq,
        "timestamp": int(time.time() * 1000)
    }

# Routes: CYU KYC Compliance
@app.post("/visor/kyc/register")
def register_kyc(req: KYCRegisterRequest):
    """Register KYC identity for wire transmission"""
    binding = CYU_VALIDATOR.register_kyc(
        req.kyc_id,
        req.wire_route,
        req.account_state
    )
    return binding.dict()

@app.post("/visor/cyu/transmit")
def cyu_transmit(req: CYUTransmitRequest):
    """Submit CYU transmission with KYC validation"""
    try:
        tx_id = f"{uuid.uuid4().hex[:16]}"
        transmission = CYU_VALIDATOR.validate_transmission(
            tx_id,
            req.kyc_id,
            req.payload
        )
        return transmission.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/visor/cyu/settle/{tx_id}")
def cyu_settle(tx_id: str):
    """Settle CYU transmission after verification"""
    # Find transmission by tx_id
    for tx in CYU_VALIDATOR.transmission_log:
        if tx.tx_id == tx_id:
            settled = CYU_VALIDATOR.settle_transmission(tx)
            return {"tx_id": tx_id, "settled": settled, "status": tx.status}
    
    raise HTTPException(status_code=404, detail="Transmission not found")

@app.get("/visor/cyu/history/{kyc_id}")
def get_cyu_history(kyc_id: str):
    """Get CYU transmission history for KYC ID"""
    history = CYU_VALIDATOR.get_transmission_history(kyc_id)
    return {
        "kyc_id": kyc_id,
        "transmissions": [t.dict() for t in history],
        "timestamp": int(time.time() * 1000)
    }

# Health check
@app.get("/health")
def health():
    return {"status": "ok", "service": "caprise-visor", "version": "1.0.0"}
