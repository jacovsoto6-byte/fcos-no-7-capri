"""CYU V3: KYC-compliant variable validation vector for wire transmission"""
import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from enum import Enum
from .schemas import KYCBinding, CYUTransmission

class AccountState(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    RESTRICTED = "restricted"
    CLOSED = "closed"

class TransmissionStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    ROUTED = "routed"
    SETTLED = "settled"
    REJECTED = "rejected"

class CYUValidator:
    """KYC compliance and variable validation for money transmission"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.kyc_registry = {}  # kyc_id -> KYCBinding
        self.transmission_log = []
    
    def register_kyc(self, kyc_id: str, wire_route: str, account_state: str = "pending") -> KYCBinding:
        """Register a KYC identity for wire transmission"""
        now = int(time.time() * 1000)
        validation_vector = self._compute_v3_vector(kyc_id)
        
        binding = KYCBinding(
            kyc_id=kyc_id,
            validation_vector=validation_vector,
            wire_route=wire_route,
            compliance_ts=now,
            account_state=account_state
        )
        
        self.kyc_registry[kyc_id] = binding
        return binding
    
    def validate_transmission(self, tx_id: str, kyc_id: str, payload: Dict[str, Any]) -> CYUTransmission:
        """Create and validate a CYU transmission"""
        if kyc_id not in self.kyc_registry:
            raise ValueError(f"KYC ID not registered: {kyc_id}")
        
        kyc = self.kyc_registry[kyc_id]
        
        # Check account state
        if kyc.account_state not in [AccountState.ACTIVE.value, AccountState.PENDING.value]:
            raise ValueError(f"Account state not eligible: {kyc.account_state}")
        
        now = int(time.time() * 1000)
        
        # Compute V3 validation vector
        validation_vector_v3 = self._compute_v3_with_payload(kyc_id, payload, now)
        
        # Compute wire signature (HMAC)
        wire_signature = self._compute_signature(tx_id, kyc_id, payload, validation_vector_v3)
        
        transmission = CYUTransmission(
            tx_id=tx_id,
            kyc_binding=kyc,
            payload=payload,
            validation_vector_v3=validation_vector_v3,
            wire_signature=wire_signature,
            timestamp=now,
            status=TransmissionStatus.VALIDATED.value
        )
        
        self.transmission_log.append(transmission)
        return transmission
    
    def _compute_v3_vector(self, kyc_id: str) -> str:
        """Compute base V3 validation vector (SHA256)"""
        return hashlib.sha256(f"{kyc_id}:{self.secret_key}".encode()).hexdigest()
    
    def _compute_v3_with_payload(self, kyc_id: str, payload: Dict[str, Any], timestamp: int) -> str:
        """Compute V3 vector with payload and timestamp"""
        payload_str = str(sorted(payload.items()))
        combined = f"{kyc_id}:{payload_str}:{timestamp}:{self.secret_key}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _compute_signature(self, tx_id: str, kyc_id: str, payload: Dict[str, Any], vector: str) -> str:
        """Compute HMAC wire signature"""
        message = f"{tx_id}:{kyc_id}:{vector}".encode()
        signature = hmac.new(
            self.secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, transmission: CYUTransmission) -> bool:
        """Verify wire transmission signature"""
        expected_sig = self._compute_signature(
            transmission.tx_id,
            transmission.kyc_binding.kyc_id,
            transmission.payload,
            transmission.validation_vector_v3
        )
        return hmac.compare_digest(expected_sig, transmission.wire_signature)
    
    def settle_transmission(self, transmission: CYUTransmission) -> bool:
        """Settle transmission after verification"""
        if not self.verify_signature(transmission):
            transmission.status = TransmissionStatus.REJECTED.value
            return False
        
        transmission.status = TransmissionStatus.SETTLED.value
        return True
    
    def get_transmission_history(self, kyc_id: Optional[str] = None) -> list:
        """Retrieve transmission audit log"""
        if kyc_id:
            return [t for t in self.transmission_log if t.kyc_binding.kyc_id == kyc_id]
        return self.transmission_log
