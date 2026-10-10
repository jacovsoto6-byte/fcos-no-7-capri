"""REST API routes for Legal Compliance & Liability Framework"""
from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal
import uuid
import time

from visor.core.liability_framework import (
    LiabilityFramework, LegalActor, ConsentType, MovementType, ParticipantRole
)
from visor.api.routes import app

# Initialize liability framework
LIABILITY_FRAMEWORK = LiabilityFramework(secret_key="liability-framework-v1")

# Request models
class LegalActorRequest(BaseModel):
    entity_id: str
    entity_name: str
    entity_type: Literal["individual", "business", "custodian", "regulator"]
    kyc_verified: bool
    jurisdiction: str
    signing_authority: str

class ConsentRequest(BaseModel):
    participant_id: str
    consent_type: str  # opt_in, opt_out, conditional, delegated
    movement_type: str  # fund_transfer, data_clearing, settlement, escrow, recovery
    scope: Dict[str, Any]
    effective_until_days: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None

class IndemnitySectionRequest(BaseModel):
    participant_id: str
    waiver_text: str

class MovementAuthRequest(BaseModel):
    consent_id: str
    movement_details: Dict[str, Any]

class MovementAckRequest(BaseModel):
    authorization_id: str
    movement_result: Dict[str, Any]

class ConsentRevokeRequest(BaseModel):
    consent_id: str
    reason: str

# Routes: Legal Actor Registration
@app.post("/legal/participants/register")
def register_legal_actor(req: LegalActorRequest):
    """Register a legal actor (individual, business, custodian, regulator)"""
    actor = LegalActor(
        entity_id=req.entity_id,
        entity_name=req.entity_name,
        entity_type=req.entity_type,
        kyc_verified=req.kyc_verified,
        kyc_timestamp=int(time.time() * 1000),
        jurisdiction=req.jurisdiction,
        signing_authority=req.signing_authority
    )
    
    result = LIABILITY_FRAMEWORK.register_participant(actor)
    return result

@app.get("/legal/participants/{entity_id}")
def get_participant(entity_id: str):
    """Retrieve legal actor registration"""
    if entity_id not in LIABILITY_FRAMEWORK.participant_registry:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    actor = LIABILITY_FRAMEWORK.participant_registry[entity_id]
    return {
        "entity_id": actor.entity_id,
        "entity_name": actor.entity_name,
        "entity_type": actor.entity_type,
        "kyc_verified": actor.kyc_verified,
        "kyc_timestamp": actor.kyc_timestamp,
        "jurisdiction": actor.jurisdiction,
        "signing_authority": actor.signing_authority
    }

# Routes: Consent Management
@app.post("/legal/consent/issue")
def issue_consent(req: ConsentRequest):
    """Issue a consent record (legally binding)"""
    try:
        consent = LIABILITY_FRAMEWORK.issue_consent(
            participant_id=req.participant_id,
            consent_type=ConsentType(req.consent_type),
            movement_type=MovementType(req.movement_type),
            scope=req.scope,
            effective_until_days=req.effective_until_days,
            conditions=req.conditions
        )
        
        return {
            "consent_id": consent.consent_id,
            "participant_id": consent.participant.entity_id,
            "consent_type": consent.consent_type.value,
            "movement_type": consent.movement_type.value,
            "scope": consent.scope,
            "effective_from": consent.effective_from,
            "effective_until": consent.effective_until,
            "cryptographic_binding": consent.cryptographic_binding,
            "timestamp_created": consent.timestamp_created,
            "status": "active"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/legal/consent/{consent_id}")
def get_consent(consent_id: str):
    """Retrieve consent record"""
    if consent_id not in LIABILITY_FRAMEWORK.consent_registry:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    consent = LIABILITY_FRAMEWORK.consent_registry[consent_id]
    return {
        "consent_id": consent.consent_id,
        "participant_id": consent.participant.entity_id,
        "consent_type": consent.consent_type.value,
        "movement_type": consent.movement_type.value,
        "scope": consent.scope,
        "effective_from": consent.effective_from,
        "effective_until": consent.effective_until,
        "conditions": consent.conditions,
        "timestamp_created": consent.timestamp_created,
        "revocation_reason": consent.revocation_reason,
        "audit_trail_count": len(consent.audit_trail)
    }

@app.post("/legal/consent/{consent_id}/revoke")
def revoke_consent(consent_id: str, req: ConsentRevokeRequest):
    """Revoke a consent record"""
    try:
        result = LIABILITY_FRAMEWORK.revoke_consent(consent_id, req.reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/legal/consent/{consent_id}/audit-trail")
def get_consent_audit_trail(consent_id: str):
    """Get complete audit trail for a consent (immutable proof)"""
    try:
        trail = LIABILITY_FRAMEWORK.get_consent_audit_trail(consent_id)
        return {
            "consent_id": consent_id,
            "audit_trail": trail,
            "record_count": len(trail),
            "immutable": True,
            "timestamp": int(time.time() * 1000)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Routes: Indemnity & Liability Waiver
@app.post("/legal/indemnity/sign")
def sign_indemnity_waiver(req: IndemnitySectionRequest):
    """Participant signs indemnity waiver (liability protection for all parties)"""
    try:
        ack = LIABILITY_FRAMEWORK.sign_indemnity_waiver(
            req.participant_id,
            req.waiver_text
        )
        return {
            "participant_id": ack["participant_id"],
            "entity_name": ack["entity_name"],
            "waiver_hash": ack["waiver_hash"],
            "signature": ack["signature"],
            "timestamp": ack["timestamp"],
            "jurisdiction": ack["jurisdiction"],
            "status": ack["validity"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/legal/indemnity/{participant_id}/status")
def get_indemnity_status(participant_id: str):
    """Check if participant has signed indemnity waiver"""
    if participant_id not in LIABILITY_FRAMEWORK.indemnity_acknowledgments:
        return {"participant_id": participant_id, "indemnity_signed": False}
    
    ack = LIABILITY_FRAMEWORK.indemnity_acknowledgments[participant_id]
    return {
        "participant_id": participant_id,
        "indemnity_signed": True,
        "signed_timestamp": ack["timestamp"],
        "waiver_hash": ack["waiver_hash"],
        "jurisdiction": ack["jurisdiction"]
    }

# Routes: Movement Authorization & Acknowledgment (Permit-to-Code)
@app.post("/legal/movement/authorize")
def authorize_movement(req: MovementAuthRequest):
    """Authorize a movement based on valid consent (permit-to-code)"""
    try:
        result = LIABILITY_FRAMEWORK.authorize_movement(
            req.consent_id,
            req.movement_details
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/legal/movement/acknowledge")
def acknowledge_movement(req: MovementAckRequest):
    """Record movement acknowledgment (immutable proof of execution)"""
    try:
        ack = LIABILITY_FRAMEWORK.acknowledge_movement(
            req.authorization_id,
            req.movement_result
        )
        return ack
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/legal/movements")
def get_movement_history(participant_id: Optional[str] = None):
    """Get movement history (optionally filtered by participant)"""
    history = LIABILITY_FRAMEWORK.get_movement_history(participant_id)
    return {
        "timestamp": int(time.time() * 1000),
        "participant_id": participant_id,
        "movements": history,
        "total_count": len(history),
        "immutable_audit_trail": True
    }

@app.get("/legal/movements/{authorization_id}")
def get_movement_details(authorization_id: str):
    """Get details of a specific movement"""
    for movement in LIABILITY_FRAMEWORK.movement_log:
        if movement.get("authorization_id") == authorization_id:
            return {
                "timestamp": int(time.time() * 1000),
                "movement": movement,
                "immutable": True
            }
    
    raise HTTPException(status_code=404, detail="Movement not found")
