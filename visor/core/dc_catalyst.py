"""DC: Data Capture & Catalyst - delta detection and action generation"""
from typing import Dict, Any, Optional
import uuid
import time
from .schemas import StateSnapshot, CatalystAction, CatalystActionStatus, CatalystActionType

class DCProvider:
    """Captures state deltas and generates catalyst actions"""
    
    def __init__(self):
        self.capture_log = []
        self.last_state = None
        self.action_history = []
    
    def capture(self, snapshot: StateSnapshot) -> StateSnapshot:
        """Compute delta and detect changes"""
        if self.last_state is None:
            # First capture: all state is delta
            snapshot.delta = snapshot.state.copy()
        else:
            # Compute delta: keys that changed
            snapshot.delta = {}
            for key in snapshot.state.keys():
                if snapshot.state.get(key) != self.last_state.get(key):
                    snapshot.delta[key] = snapshot.state.get(key)
            
            # Also capture keys that were deleted
            for key in self.last_state.keys():
                if key not in snapshot.state:
                    snapshot.delta[key] = None
        
        self.capture_log.append(snapshot)
        self.last_state = snapshot.state.copy() if snapshot.state else {}
        return snapshot
    
    def catalyst(self, snapshot: StateSnapshot) -> Optional[CatalystAction]:
        """Generate action based on state and health"""
        action = None
        
        if snapshot.health == HealthStatus.STALE:
            action = self._create_action(CatalystActionType.RECOVER, snapshot)
        elif snapshot.delta:
            action = self._create_action(CatalystActionType.PROPAGATE, snapshot)
        
        if action:
            self.action_history.append(action)
        
        return action
    
    def _create_action(self, action_type: CatalystActionType, snapshot: StateSnapshot) -> CatalystAction:
        """Create a catalyst action"""
        now = int(time.time() * 1000)
        action_id = uuid.uuid4().hex[:16]
        
        return CatalystAction(
            id=action_id,
            type=action_type,
            timestamp=now,
            source="DC",
            status=CatalystActionStatus.PENDING,
            result=None
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return DC metrics"""
        return {
            "captures": len(self.capture_log),
            "actions_generated": len(self.action_history),
            "last_delta_keys": list(self.capture_log[-1].delta.keys()) if self.capture_log else []
        }
