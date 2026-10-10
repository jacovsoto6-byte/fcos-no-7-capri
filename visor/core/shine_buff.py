"""Shine Buff: Data refinement and hallucination removal layer"""
from typing import Dict, Any, Optional
from pydantic import ValidationError
from .schemas import StateSnapshot, CatalystAction

class ShineBuff:
    """Polishes and validates data to remove ambiguity and hallucination"""
    
    @staticmethod
    def polish_state(raw_state: Dict[str, Any]) -> Dict[str, Any]:
        """Remove null, undefined, and floating values; enforce types"""
        polished = {}
        
        for key, value in raw_state.items():
            # Skip None/null
            if value is None:
                continue
            
            # Enforce numeric precision
            if isinstance(value, float):
                polished[key] = round(value, 6)  # 6 decimal places
            elif isinstance(value, bool):
                polished[key] = value
            elif isinstance(value, (int, str)):
                polished[key] = value
            elif isinstance(value, dict):
                polished[key] = ShineBuff.polish_state(value)
            elif isinstance(value, (list, tuple)):
                polished[key] = [v for v in value if v is not None]
        
        return polished
    
    @staticmethod
    def validate_snapshot(snapshot: Dict[str, Any]) -> bool:
        """Strict validation using Pydantic schemas"""
        try:
            StateSnapshot(**snapshot)
            return True
        except ValidationError:
            return False
    
    @staticmethod
    def validate_action(action: Dict[str, Any]) -> bool:
        """Validate catalyst action schema"""
        try:
            CatalystAction(**action)
            return True
        except ValidationError:
            return False
    
    @staticmethod
    def sanitize_for_transmission(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove any non-serializable or sensitive data before transmission"""
        sanitized = {}
        
        for key, value in data.items():
            # Skip private keys
            if key.startswith('_'):
                continue
            
            # Only allow JSON-serializable types
            if isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = ShineBuff.sanitize_for_transmission(value)
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [v for v in value if isinstance(v, (str, int, float, bool, type(None)))]
        
        return sanitized
