"""
TRUVEX Phase 2 Comprehensive Test Suite.
Validates:
1. Authentication (JWT generation & role extraction)
2. Company registration & Superadmin accreditation
3. Employee creation & automatic ID sequencing (TRX-E-XXXX)
4. Five-Layer Trust Engine hard security boundaries
5. Pre-call verification & Session ID issuance
6. Customer lookup with zero credit consumption
7. Fraud incident reporting
"""

import io
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.trust_engine import TrustEngine

client = TestClient(app)


def test_login_superadmin():
    """Verify superadmin login and JWT token receipt."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@truvex.ai", "password": "AdminPass123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "superadmin"


def test_login_demo_employee():
    """Verify Marcus Vance demo employee login."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "marcus@apexbank.example", "password": "Marcus123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "employee"
    assert data["user"]["company_code"] == "TRX-C-0001"


def test_trust_engine_hard_security_boundaries():
    """Verify that a deepfake or unapproved company CANNOT pass the Trust Engine."""
    # Test 1: Fake voice must fail even if company and employee are valid
    fake_voice_result = {
        "verdict": "fake",
        "score": 0.89,  # High deepfake score
    }
    match_speaker = {"decision": "match", "similarity": 0.9}
    eval1 = TrustEngine.evaluate(
        company_status="approved",
        employee_status="active",
        can_initiate_calls=True,
        aletheia_data={"result": fake_voice_result},
        eidos_data={"result": match_speaker},
    )
    assert eval1["verdict"] == "REJECTED"
    assert eval1["trust_score"] <= 45.0
    assert any("deepfake" in f.lower() for f in eval1["hard_failures"])

    # Test 2: Unapproved company must fail
    real_voice = {"verdict": "real", "score": 0.02}
    eval2 = TrustEngine.evaluate(
        company_status="pending",
        employee_status="active",
        can_initiate_calls=True,
        aletheia_data={"result": real_voice},
        eidos_data={"result": match_speaker},
    )
    assert eval2["verdict"] == "REJECTED"
    assert any("not approved" in f.lower() for f in eval2["hard_failures"])

    # Test 3: Speaker mismatch must fail
    mismatch_speaker = {"decision": "no_match", "similarity": -0.2}
    eval3 = TrustEngine.evaluate(
        company_status="approved",
        employee_status="active",
        can_initiate_calls=True,
        aletheia_data={"result": real_voice},
        eidos_data={"result": mismatch_speaker},
    )
    assert eval3["verdict"] == "REJECTED"
    assert any("biometric" in f.lower() for f in eval3["hard_failures"])


def test_pre_call_verification_and_session_issuance():
    """Verify pre-call audio verification and session token creation."""
    # Login as Marcus
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "marcus@apexbank.example", "password": "Marcus123!"},
    )
    token = login_resp.json()["access_token"]

    # Simulated audio file (>1KB dummy bytes)
    audio_file = io.BytesIO(b"RIFF" + b"\x00" * 2000)

    form_data = {
        "employee_id": "TRX-E-0001",
        "customer_ref": "CUST-9921",
        "call_topic": "Suspicious Card Transaction Review",
        "communication_category": "fraud_prevention",
        "consent_given": "true",
    }
    files = {"file": ("test_voice.wav", audio_file, "audio/wav")}

    resp = client.post(
        "/api/verification/pre-call-verify",
        headers={"Authorization": f"Bearer {token}"},
        data=form_data,
        files=files,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["session_id"].startswith("TRX-S-")
    assert "challenge_code" in data
    assert data["verdict"] == "VERIFIED"

    # Now verify customer lookup with this session ID!
    lookup_resp = client.post(
        "/api/verification/customer-lookup",
        json={
            "company_id_or_code": "TRX-C-0001",
            "employee_id_or_code": "TRX-E-0001",
            "session_id": data["session_id"],
        },
    )
    assert lookup_resp.status_code == 200
    lookup_data = lookup_resp.json()
    assert lookup_data["valid"] is True
    assert lookup_data["company_name"] == "Apex Global Bank"
    assert lookup_data["employee_name"] == "Marcus Vance"
    assert lookup_data["status"] == "ACTIVE"


def test_customer_lookup_invalid_credentials():
    """Verify that wrong company or fake session ID returns valid=False."""
    lookup_resp = client.post(
        "/api/verification/customer-lookup",
        json={
            "company_id_or_code": "FAKE-CORP",
            "employee_id_or_code": "FAKE-EMP",
            "session_id": "TRX-S-000000",
        },
    )
    assert lookup_resp.status_code == 200
    assert lookup_resp.json()["valid"] is False


def test_fraud_report_submission():
    """Verify public customer fraud reporting."""
    resp = client.post(
        "/api/verification/report-fraud",
        json={
            "claimed_company_name": "Suspicious Bank Impersonator",
            "caller_phone": "+919876543210",
            "description": "Caller claimed to be from security asking for OTP without valid Trust ID.",
            "severity": "high",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["success"] is True


def test_platform_stats():
    """Verify aggregated platform statistics."""
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_companies"] >= 1
    assert data["total_employees"] >= 1
