"""AM: Adaptive Manager - refresh cycle and health validation"""
import time
from typing import Dict, Any
from .schemas import StateSnapshot, HealthStatus

class AMProvider:
    """Manages state refresh rate and health validation"""
    
    def __init__(self, refresh_hz: float = 10.0, stale_after_ms: int = 500):
        self.refresh_hz = refresh_hz
        self.stale_after_ms = stale_after_ms
        self.last_refresh = 0.0
        self.refresh_cycle_count = 0
    
    def refresh(self, source_state: Dict[str, Any], seq: int) -> StateSnapshot:
        """Perform a refresh cycle and return snapshot"""
        now = int(time.time() * 1000)  # ms precision
        self.last_refresh = now
        self.refresh_cycle_count += 1
        
        snapshot = StateSnapshot(
            timestamp=now,
            seq=seq,
            state=source_state.copy(),
            delta={},
            health=HealthStatus.STABLE
        )
        return snapshot
    
    def validate(self, snapshot: StateSnapshot) -> bool:
        """Check if snapshot is fresh (not stale)"""
        now = int(time.time() * 1000)
        age_ms = now - snapshot.timestamp
        
        if age_ms > self.stale_after_ms:
            snapshot.health = HealthStatus.STALE
            return False
        
        snapshot.health = HealthStatus.STABLE
        return True
    
    def get_health(self) -> Dict[str, Any]:
        """Return AM health metrics"""
        return {
            "refresh_hz": self.refresh_hz,
            "stale_after_ms": self.stale_after_ms,
            "cycle_count": self.refresh_cycle_count,
            "last_refresh_ms_ago": int(time.time() * 1000) - self.last_refresh
        }
