# Caprise Visor Legal Compliance Framework

## Overview

The **Legal Compliance & Liability Framework** provides institutional-grade documentation and protection for all parties in:

- **Fund Transfers** — money movement with full authorization trail
- **Data Clearing** — information transfer with consent binding
- **Settlement** — finality with immutable proof
- **Escrow** — conditional holding with documented terms
- **Recovery** — reversal with full audit visibility

---

## Core Concepts

### 1. **Liability Protection**

✅ **Immutable Audit Trail** — Every action documented, timestamped, cryptographically signed  
✅ **Consent Proof** — Participant explicitly authorized (or withheld) consent  
✅ **Indemnity Waiver** — All parties acknowledge risks and waive liability within scope  
✅ **Non-Repudiation** — Participant cannot deny they authorized something

### 2. **Indemnity Waiver System**

Participants sign a waiver that states:

> *"I understand the risks of this transaction. I authorize this movement of funds/data. I acknowledge intermediaries acting in good faith are not liable for losses. I accept legal and financial responsibility for my participation."*

**Result:**
- Originator cannot sue intermediary for market loss
- Beneficiary cannot claim non-receipt if settled on-chain
- Custodian has documented proof of authorization
- Regulator has full visibility into who authorized what

### 3. **Consent Management**

Four types of consent:

```
📝 OPT_IN:       Participant explicitly agrees to movement
🚫 OPT_OUT:      Participant explicitly refuses (withholding)
🔒 CONDITIONAL:  Participant agrees only if conditions met (e.g., amount ≤ $50K)
👤 DELEGATED:    Participant authorizes on behalf of another entity
```

### 4. **Permit-to-Code**

Movements execute **only** after:

1. ✅ Participant registered (KYC verified)
2. ✅ Consent issued (legally binding)
3. ✅ Indemnity waiver signed
4. ✅ Movement authorized (all conditions met)
5. ✅ Code execution permitted (green light)

### 5. **Movement Acknowledgment**

After execution:

- ✅ Movement is immutable (cannot be undone without new consent)
- ✅ All parties have **equal visibility** (originator, beneficiary, intermediary)
- ✅ Cryptographic proof confirms it happened
- ✅ No party can deny they knew about it

---

## REST API: Legal Framework Routes

### Participant Registration

**Register a legal actor:**
```bash
POST /legal/participants/register
Content-Type: application/json

{
  "entity_id": "bank_acme_v1",
  "entity_name": "ACME Bank Inc.",
  "entity_type": "business",
  "kyc_verified": true,
  "jurisdiction": "US_NY",
  "signing_authority": "cfo_john_smith"
}
```

**Response:**
```json
{
  "entity_id": "bank_acme_v1",
  "status": "registered",
  "timestamp": 1728553200000,
  "kyc_status": "verified"
}
```

### Consent Issuance

**Issue consent (binding legal document):**
```bash
POST /legal/consent/issue

{
  "participant_id": "bank_acme_v1",
  "consent_type": "opt_in",
  "movement_type": "fund_transfer",
  "scope": {
    "amount_cents": 5000000,
    "currency": "USD",
    "beneficiary": "bank_xyz_v1",
    "purpose": "Payment for invoice INV-2026-001"
  },
  "effective_until_days": 30,
  "conditions": null
}
```

**Response:**
```json
{
  "consent_id": "a1b2c3d4e5f6g7h8",
  "participant_id": "bank_acme_v1",
  "consent_type": "opt_in",
  "movement_type": "fund_transfer",
  "scope": {...},
  "effective_from": 1728553200000,
  "effective_until": 1731145200000,
  "cryptographic_binding": "sha256_hmac_signature_here",
  "timestamp_created": 1728553200000,
  "status": "active"
}
```

### Indemnity Waiver

**Participant signs waiver (liability protection):**
```bash
POST /legal/indemnity/sign

{
  "participant_id": "bank_acme_v1",
  "waiver_text": "I acknowledge I am participating in this transaction at my own risk. I have read and understand the terms. I waive claims against intermediaries acting in good faith. My signature below constitutes full and binding consent and acceptance of all terms."
}
```

**Response:**
```json
{
  "participant_id": "bank_acme_v1",
  "entity_name": "ACME Bank Inc.",
  "waiver_hash": "sha256_hash_of_waiver_text",
  "signature": "hmac_signature_proof",
  "timestamp": 1728553200000,
  "jurisdiction": "US_NY",
  "status": "valid"
}
```

### Movement Authorization (Permit-to-Code)

**Authorize movement (legal permission to execute):**
```bash
POST /legal/movement/authorize

{
  "consent_id": "a1b2c3d4e5f6g7h8",
  "movement_details": {
    "amount_cents": 5000000,
    "currency": "USD",
    "originator": "bank_acme_v1",
    "beneficiary": "bank_xyz_v1",
    "settlement_method": "fedwire"
  }
}
```

**Response:**
```json
{
  "permit_to_code": true,
  "authorization_id": "c3d4e5f6g7h8i9j0",
  "consent_id": "a1b2c3d4e5f6g7h8",
  "movement_type": "fund_transfer",
  "timestamp": 1728553200000,
  "valid_until": 1731145200000,
  "proceed_with_execution": true
}
```

**Now smart contract / code can execute:**
```python
if auth["permit_to_code"] == true:
    # Execute movement (fund transfer, data clear, settlement, etc.)
    execute_movement(auth["authorization_id"], movement_data)
```

### Movement Acknowledgment

**Record acknowledgment (immutable proof of execution):**
```bash
POST /legal/movement/acknowledge

{
  "authorization_id": "c3d4e5f6g7h8i9j0",
  "movement_result": {
    "status": "executed",
    "txn_id": "fedwire_20261010_123456",
    "settlement_time": 1728553260000,
    "confirmation_reference": "CFM-20261010-789"
  }
}
```

**Response:**
```json
{
  "acknowledgment_id": "d4e5f6g7h8i9j0k1",
  "authorization_id": "c3d4e5f6g7h8i9j0",
  "movement_result": {...},
  "acknowledgment_signature": "hmac_proof_of_ack",
  "timestamp": 1728553260000,
  "status": "acknowledged",
  "immutable": true,
  "all_parties_visible": true
}
```

**Key point:** Movement is now:
- ✅ Executed (happened)
- ✅ Acknowledged (all parties know)
- ✅ Immutable (cannot be undone)
- ✅ Visible (originator, beneficiary, intermediary, regulator all see it)

### Audit Trail

**Get full consent audit trail (immutable proof):**
```bash
GET /legal/consent/{consent_id}/audit-trail
```

**Response:**
```json
{
  "consent_id": "a1b2c3d4e5f6g7h8",
  "audit_trail": [
    {
      "authorization_id": "c3d4e5f6g7h8i9j0",
      "consent_id": "a1b2c3d4e5f6g7h8",
      "participant": "bank_acme_v1",
      "movement_details": {...},
      "timestamp": 1728553200000,
      "status": "authorized",
      "permit_to_code": true
    },
    {...more entries...}
  ],
  "record_count": 42,
  "immutable": true,
  "timestamp": 1728553300000
}
```

**Get movement history:**
```bash
GET /legal/movements?participant_id=bank_acme_v1
```

---

## Example: Full Consent-to-Settlement Flow

### Step 1: Register Participants

```bash
# Register originator
POST /legal/participants/register
{"entity_id": "bank_acme", "entity_name": "ACME Bank", ...}

# Register beneficiary
POST /legal/participants/register
{"entity_id": "bank_xyz", "entity_name": "XYZ Bank", ...}

# Register intermediary (clearing house)
POST /legal/participants/register
{"entity_id": "fedwire_clearing", "entity_name": "Federal Reserve", ...}
```

### Step 2: Issue Consent

```bash
POST /legal/consent/issue
{
  "participant_id": "bank_acme",
  "consent_type": "opt_in",
  "movement_type": "fund_transfer",
  "scope": {
    "amount_cents": 50000000,
    "currency": "USD",
    "beneficiary": "bank_xyz"
  },
  "effective_until_days": 30
}

Response: consent_id = "abc123"
```

### Step 3: Sign Indemnity Waiver

```bash
POST /legal/indemnity/sign
{
  "participant_id": "bank_acme",
  "waiver_text": "[Full waiver text acknowledging risks and authorizing transaction]"
}

Response: waiver_hash = "xyz789", signature = "hmac_proof"
```

### Step 4: Authorize Movement

```bash
POST /legal/movement/authorize
{
  "consent_id": "abc123",
  "movement_details": {
    "amount_cents": 50000000,
    "originator": "bank_acme",
    "beneficiary": "bank_xyz"
  }
}

Response: permit_to_code = true, authorization_id = "auth456"
```

### Step 5: Execute (Smart Contract / Code)

```python
if authorization["permit_to_code"]:
    # Federal Reserve / clearing house executes transfer
    result = fedwire_transfer(
        amount=500000.00,
        from_account="acme_123456789",
        to_account="xyz_987654321"
    )
    # result = {"txn_id": "FW_20261010_789", "status": "settled", ...}
```

### Step 6: Acknowledge Movement

```bash
POST /legal/movement/acknowledge
{
  "authorization_id": "auth456",
  "movement_result": {
    "status": "executed",
    "txn_id": "FW_20261010_789",
    "settlement_time": 1728553260000
  }
}

Response: acknowledgment_id = "ack789", immutable = true, all_parties_visible = true
```

### Step 7: Query Audit Trail

```bash
GET /legal/movements?participant_id=bank_acme
```

Result: Complete history from consent → waiver → authorization → execution → acknowledgment, all immutable and cryptographically signed.

---

## Legal Protections Summary

| Protection | How It Works | Beneficiary |
|---|---|---|
| **Liability Shield** | Immutable consent + indemnity waiver | All parties (esp. intermediaries) |
| **Non-Repudiation** | HMAC signature proves participant authorized | Regulator, beneficiary |
| **Audit Trail** | Every action logged, timestamped, signed | Compliance, disputes |
| **Consent Binding** | Legal document with cryptographic proof | Originator, beneficiary |
| **Revocation Trail** | Consent can be revoked with new immutable record | Originator (protection from fraud) |
| **Conditional Logic** | Consent enforced by code (can't execute outside terms) | Beneficiary (protection) |
| **Settlement Finality** | Acknowledgment creates immutable proof of execution | All parties (no dispute) |
| **Permit-to-Code** | Movement only executes if legally authorized | System integrity |
| **All-Parties-Visible** | No hidden movements, everyone sees settlement | Regulator, fraud prevention |

---

## Compliance with Regulations

✅ **GDPR** — Consent explicitly documented, can be revoked, audit trail available  
✅ **HIPAA** — All movements and data transfers require documented consent  
✅ **SOX** — Immutable audit trail of all transactions and approvals  
✅ **OFAC** — Every participant registered with KYC verification  
✅ **Wire Act** — Permit-to-code ensures authorization before execution  
✅ **ACH/NACHA** — Full origination disclosure and consent proof  
✅ **MiFID II** (EU) — Detailed record of participant intent and authorization  

---

## Key Features

🔒 **Cryptographic Binding** — HMAC signatures prove authenticity, no forgery  
🔒 **Immutable Log** — All records permanent, tamper-proof, timestamped  
🔒 **Equal Visibility** — Originator, beneficiary, intermediary, regulator all see same data  
🔒 **Conditional Execution** — Code can only run if legal conditions met  
🔒 **Revocation Trail** — Consent can be withdrawn, new immutable record created  
🔒 **Non-Repudiation** — Participant cannot deny they authorized something  
🔒 **Permit-to-Code** — Green light from legal layer → code execution  
🔒 **Movement Acknowledgment** — Cryptographic proof that movement happened + all parties know  

---

## Version

**v1.0.0** — Stable Release  
**Date**: 2026-10-10  
**Status**: Production Ready
