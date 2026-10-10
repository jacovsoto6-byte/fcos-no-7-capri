"""Caprise Visor - Startup and server configuration"""
import uvicorn
from api.routes import app, CAPRISE, AM, DC
import time
from typing import Dict, Any

def dummy_state_provider() -> Dict[str, Any]:
    """Provide simulated state for demo"""
    return {
        "timestamp": int(time.time() * 1000),
        "voltage": 230.0 + (time.time() % 5) * 0.1,
        "current": 14.5 + (time.time() % 3) * 0.2,
        "temperature": 62.4,
        "status": "running"
    }

def setup_handlers():
    """Register action handlers"""
    def handle_recover(action):
        print(f"[Handler] Recovering from stale state: {action.id}")
        return {"recovered": True}
    
    def handle_propagate(action):
        print(f"[Handler] Propagating delta: {action.id}")
        return {"propagated": True}
    
    CAPRISE.register_action_handler("recover", handle_recover)
    CAPRISE.register_action_handler("propagate", handle_propagate)

if __name__ == "__main__":
    # Setup
    setup_handlers()
    
    # Start PACE event loop in background
    CAPRISE.run_loop(dummy_state_provider, interval_s=0.1)
    
    # Start REST server
    print("\n" + "="*60)
    print("Caprise Visor v1.0.0")
    print("Multi-Runtime Control Plane")
    print("REST API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
