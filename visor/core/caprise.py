"""Caprise: Main orchestrator - PACE runtime event loop"""
import time
import threading
from typing import Dict, Any, Optional, Callable
from .am_manager import AMProvider
from .dc_catalyst import DCProvider
from .schemas import StateSnapshot, CatalystAction, HealthStatus

class Caprise:
    """PACE Runtime: Parallel, Adaptive, Catalyst, Event-driven"""
    
    def __init__(self, am: AMProvider, dc: DCProvider):
        self.am = am
        self.dc = dc
        self.state = {}
        self.seq = 0
        self.running = False
        self.loop_thread = None
        self.action_handlers: Dict[str, Callable] = {}
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a handler for catalyst actions"""
        self.action_handlers[action_type] = handler
    
    def refresh_cycle(self, raw_state: Dict[str, Any]) -> Optional[CatalystAction]:
        """Single CLEAR cycle: Capture → Log → Execute → Audit → Report"""
        self.seq += 1
        
        # CAPTURE: AM refresh
        snapshot = self.am.refresh(raw_state, self.seq)
        
        # VALIDATE: AM health check
        self.am.validate(snapshot)
        
        # LOG: DC capture (immutable log)
        snapshot = self.dc.capture(snapshot)
        
        # EXECUTE: DC catalyst generates action
        action = self.dc.catalyst(snapshot)
        
        # UPDATE: Internal state
        self.state = snapshot.state.copy()
        
        # AUDIT: Action history is maintained in DC
        # REPORT: State is queryable
        
        return action
    
    def handle_action(self, action: Optional[CatalystAction]):
        """Execute catalyst action if handler is registered"""
        if not action:
            return
        
        if action.type.value in self.action_handlers:
            try:
                result = self.action_handlers[action.type.value](action)
                action.result = result
                action.status = "executed"
            except Exception as e:
                action.status = "failed"
                action.result = {"error": str(e)}
    
    def run_loop(self, state_provider: Callable, interval_s: float = 0.1):
        """Run PACE event loop (non-blocking thread)"""
        if self.running:
            return
        
        self.running = True
        
        def _loop():
            while self.running:
                try:
                    raw_state = state_provider()
                    action = self.refresh_cycle(raw_state)
                    self.handle_action(action)
                    time.sleep(interval_s)
                except Exception as e:
                    print(f"[Caprise] Loop error: {e}")
                    time.sleep(interval_s)
        
        self.loop_thread = threading.Thread(target=_loop, daemon=True)
        self.loop_thread.start()
    
    def stop(self):
        """Stop PACE event loop"""
        self.running = False
        if self.loop_thread:
            self.loop_thread.join(timeout=1.0)
    
    def get_state(self) -> Dict[str, Any]:
        """Query current state"""
        return self.state.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics from AM + DC"""
        return {
            "seq": self.seq,
            "am": self.am.get_health(),
            "dc": self.dc.get_metrics(),
            "running": self.running
        }
