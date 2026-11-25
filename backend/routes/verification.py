"""
TRUVEX Session Verification, Five-Layer Trust Engine & Customer Portal Routes.
Owner: Rounit / Anany
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import AuditLog, Company, Employee, FraudReport, TrustSession, User
from backend.routes.auth import get_current_user
from backend.schemas import (
    ChallengeConfirmRequest,
    CustomerLookupRequest,
    CustomerLookupResponse,
    FraudReportCreate,
    SessionResponse,
)
from backend.services.aletheia import AletheiaClient
from backend.services.eidos import EidosClient
from backend.services.trust_engine import TrustEngine

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.post("/pre-call-verify", response_model=SessionResponse)
async def pre_call_verify(
    employee_id: str = Form(...),
    customer_ref: str = Form(...),
    call_topic: str = Form(...),
    communication_category: str = Form("fraud_prevention"),
    consent_given: bool = Form(True),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Employee pre-call authentication and live voice screening.
    Evaluates:
      1. Company approval
      2. Employee identity & status
      3. Aletheia deepfake detection
      4. Eidos biometric speaker verification
      5. Communication authority
    Generates a cryptographically secure temporary Session ID (10-min TTL).
    """
    if not consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice verification requires explicit consent.",
        )

    # 1. Fetch Employee and Company
    emp = (
        db.query(Employee)
        .filter((Employee.id == employee_id) | (Employee.employee_code == employee_id))
        .first()
    )
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

    comp = db.query(Company).filter(Company.id == emp.company_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated company not found.")

    audio_bytes = await file.read()
    if len(audio_bytes) < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio recording is empty or corrupt.",
        )

    # 2. Run DetectifAI Aletheia (Deepfake Detection)
    aletheia_client = AletheiaClient()
    aletheia_result = await aletheia_client.detect_deepfake(
        audio_bytes=audio_bytes,
        filename=file.filename or "pre_call.wav",
        content_type=file.content_type or "audio/wav",
    )

    # 3. Run DetectifAI Eidos (Speaker Verification)
    eidos_client = EidosClient()
    eidos_result = await eidos_client.verify_speaker(
        speaker_id=emp.speaker_id,
        audio_bytes=audio_bytes,
        filename=file.filename or "pre_call.wav",
        content_type=file.content_type or "audio/wav",
    )

    # 4. Run Five-Layer Trust Engine
    eval_result = TrustEngine.evaluate(
        company_status=comp.status,
        employee_status=emp.status,
        can_initiate_calls=emp.can_initiate_calls,
        aletheia_data=aletheia_result,
        eidos_data=eidos_result,
        communication_category=communication_category,
    )

    # Check for hard security rejection
    if eval_result["verdict"] == "REJECTED":
        audit = AuditLog(
            event_type="SESSION_REJECTED",
            actor=current_user.email,
            details=f"Session attempt rejected for {emp.employee_code}. Failures: {', '.join(eval_result['hard_failures'])}",
        )
        db.add(audit)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Pre-call trust verification failed mandatory security checks.",
                "verdict": eval_result["verdict"],
                "trust_score": eval_result["trust_score"],
                "failures": eval_result["hard_failures"],
                "layer_results": eval_result["layers"],
            },
        )

    # 5. Generate secure Session ID and 4-digit Challenge Code
    session_code = f"TRX-S-{secrets.randbelow(900000) + 100000}"
    challenge_pin = f"{secrets.randbelow(9000) + 1000}"
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(minutes=10)

    # Extract score details
    al_verdict = aletheia_result.get("result", {}).get("verdict", "real")
    al_score = aletheia_result.get("result", {}).get("score", 0.03)
    ei_decision = eidos_result.get("result", {}).get("decision", "match")
    ei_similarity = eidos_result.get("result", {}).get("similarity", 0.85)

    new_session = TrustSession(
        session_id=session_code,
        company_id=comp.id,
        employee_id=emp.id,
        customer_ref=customer_ref,
        call_topic=call_topic,
        communication_category=communication_category,
        trust_score=eval_result["trust_score"],
        aletheia_verdict=al_verdict,
        aletheia_score=al_score,
        eidos_decision=ei_decision,
        eidos_similarity=ei_similarity,
        overall_verdict=eval_result["verdict"],
        challenge_code=challenge_pin,
        challenge_confirmed=False,
        status="ACTIVE",
        created_at=now_utc,
        expires_at=expires_at,
    )
    db.add(new_session)

    audit = AuditLog(
        event_type="SESSION_ISSUED",
        actor=current_user.email,
        details=f"Session {session_code} issued for employee {emp.employee_code} -> customer {customer_ref}. Trust Score: {eval_result['trust_score']}%",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "session_id": session_code,
        "trust_id": session_code,
        "trust_score": eval_result["trust_score"],
        "verdict": eval_result["verdict"],
        "challenge_code": challenge_pin,
        "expires_at": expires_at.isoformat(),
        "expires_in_seconds": 600,
        "layer_results": eval_result["layers"],
        "ai_evidence": {
            "aletheia": aletheia_result,
            "eidos": eidos_result,
        },
    }


@router.post("/customer-lookup", response_model=CustomerLookupResponse)
async def customer_lookup(payload: CustomerLookupRequest, db: Session = Depends(get_db)):
    """
    Public customer endpoint to verify caller authenticity using stored evidence (0 API credits burned).
    Validates Company ID, Employee ID, and Session ID.
    """
    comp_input = payload.company_id_or_code.strip()
    emp_input = payload.employee_id_or_code.strip()
    sess_input = payload.session_id.strip()

    # Find company
    comp = (
        db.query(Company)
        .filter((Company.company_code == comp_input) | (Company.id == comp_input))
        .first()
    )

    # Find employee
    emp = (
        db.query(Employee)
        .filter((Employee.employee_code == emp_input) | (Employee.id == emp_input))
        .first()
    )

    # Find session
    session = (
        db.query(TrustSession)
        .filter(TrustSession.session_id == sess_input)
        .first()
    )

    # Base failure response structure
    if not session or not comp or not emp or session.employee_id != emp.id or session.company_id != comp.id:
        return CustomerLookupResponse(
            valid=False,
            session_id=sess_input,
            company_name=comp.name if comp else None,
            company_code=comp.company_code if comp else None,
            company_approved=comp.status == "approved" if comp else False,
            employee_name=emp.full_name if emp else None,
            employee_code=emp.employee_code if emp else None,
            department=emp.department if emp else None,
            designation=emp.designation if emp else None,
            call_topic=session.call_topic if session else None,
            communication_category=session.communication_category if session else None,
            voice_authenticity={"passed": False, "verdict": "unknown", "score": 0.0},
            speaker_verification={"passed": False, "decision": "no_match", "similarity": 0.0},
            authority_verification=False,
            session_valid=False,
            status="INVALID_CREDENTIALS",
            trust_score=0.0,
            overall_verdict="REJECTED",
            challenge_code=None,
            remaining_seconds=0,
            expires_at="",
        )

    # Check TTL Expiration
    now_utc = datetime.now(timezone.utc)
    # Ensure timezone aware comparison
    exp = session.expires_at.replace(tzinfo=timezone.utc) if session.expires_at.tzinfo is None else session.expires_at
    remaining = int((exp - now_utc).total_seconds())

    if remaining <= 0 or session.status in ("EXPIRED", "REVOKED", "COMPLETED"):
        session.status = "EXPIRED" if session.status == "ACTIVE" else session.status
        db.commit()

        return CustomerLookupResponse(
            valid=False,
            session_id=session.session_id,
            company_name=comp.name,
            company_code=comp.company_code,
            company_approved=comp.status == "approved",
            employee_name=emp.full_name,
            employee_code=emp.employee_code,
            department=emp.department,
            designation=emp.designation,
            call_topic=session.call_topic,
            communication_category=session.communication_category,
            voice_authenticity={"passed": False, "verdict": session.aletheia_verdict, "score": session.aletheia_score},
            speaker_verification={"passed": False, "decision": session.eidos_decision, "similarity": session.eidos_similarity},
            authority_verification=False,
            session_valid=False,
            status="EXPIRED",
            trust_score=0.0,
            overall_verdict="EXPIRED_SESSION",
            challenge_code=None,
            remaining_seconds=0,
            expires_at=session.expires_at.isoformat(),
        )

    return CustomerLookupResponse(
        valid=True,
        session_id=session.session_id,
        company_name=comp.name,
        company_code=comp.company_code,
        company_approved=comp.status == "approved",
        employee_name=emp.full_name,
        employee_code=emp.employee_code,
        department=emp.department,
        designation=emp.designation,
        call_topic=session.call_topic,
        communication_category=session.communication_category,
        voice_authenticity={
            "passed": session.aletheia_verdict == "real",
            "verdict": session.aletheia_verdict,
            "score": session.aletheia_score,
            "status": "Authentic Human Voice" if session.aletheia_verdict == "real" else "Potential Synthetic / Fake",
        },
        speaker_verification={
            "passed": session.eidos_decision == "match",
            "decision": session.eidos_decision,
            "similarity": session.eidos_similarity,
            "status": "Biometric Identity Confirmed" if session.eidos_decision == "match" else "Voice Mismatch",
        },
        authority_verification=emp.can_initiate_calls,
        session_valid=True,
        status="ACTIVE",
        trust_score=session.trust_score,
        overall_verdict=session.overall_verdict,
        challenge_code=session.challenge_code,
        remaining_seconds=remaining,
        expires_at=session.expires_at.isoformat(),
    )


@router.post("/confirm-challenge")
async def confirm_challenge(payload: ChallengeConfirmRequest, db: Session = Depends(get_db)):
    """Validates mutual out-of-band confirmation between customer and representative."""
    session = (
        db.query(TrustSession)
        .filter(TrustSession.session_id == payload.session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    if session.challenge_code != payload.challenge_code.strip():
        return {
            "success": False,
            "matched": False,
            "message": "Challenge code does not match active session token.",
        }

    session.challenge_confirmed = True
    db.commit()

    return {
        "success": True,
        "matched": True,
        "message": "Session mutual challenge confirmed. Out-of-band authenticity verified.",
    }


@router.post("/end-session")
async def end_session(session_id: str = Form(...), db: Session = Depends(get_db)):
    """Terminates an active calling session."""
    session = db.query(TrustSession).filter(TrustSession.session_id == session_id).first()
    if session:
        session.status = "COMPLETED"
        db.commit()
    return {"success": True, "message": f"Session {session_id} ended."}


@router.post("/report-fraud", status_code=status.HTTP_201_CREATED)
async def report_fraud(payload: FraudReportCreate, db: Session = Depends(get_db)):
    """Submits an unverified or spoofed call incident report."""
    report = FraudReport(
        claimed_company_id=payload.claimed_company_id,
        claimed_employee_id=payload.claimed_employee_id,
        claimed_session_id=payload.claimed_session_id,
        claimed_company_name=payload.claimed_company_name,
        caller_phone=payload.caller_phone,
        description=payload.description,
        severity=payload.severity,
        status="new",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    audit = AuditLog(
        event_type="FRAUD_REPORTED",
        actor=payload.caller_phone or "Customer Portal",
        details=f"Fraud report filed against '{payload.claimed_company_name or 'Unknown'}'. Claimed Session: {payload.claimed_session_id}",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "report_id": report.id,
        "message": "Incident report registered. Security and compliance teams have been alerted.",
    }


@router.post("/test-live-ai")
async def test_live_ai(
    model: str = Form(...),
    speaker_id: str = Form("trx_spk_TRX-E-0001"),
    confirmed_live_credit_spend: bool = Form(False),
    file: UploadFile = File(...),
):
    """
    Interactive Live AI Diagnostic Sandbox.
    model choices: aletheia_detect, eidos_enroll, eidos_verify
    Requires confirmed_live_credit_spend=true to consume credits.
    """
    audio_bytes = await file.read()
    if len(audio_bytes) < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio recording is too short or corrupt.",
        )

    # Safety: refuse live calls unless explicitly confirmed
    aletheia = AletheiaClient()
    eidos = EidosClient()
    is_live = aletheia.is_live_configured()

    if is_live and not confirmed_live_credit_spend:
        return {
            "error": True,
            "code": "credit_spend_not_confirmed",
            "message": "This action would consume DetectifAI credits. Set confirmed_live_credit_spend=true to proceed.",
            "is_live_api": is_live,
        }

    if model == "aletheia_detect":
        result = await aletheia.detect_deepfake(
            audio_bytes=audio_bytes,
            filename=file.filename or "test.wav",
            content_type=file.content_type or "audio/wav",
        )
    elif model == "eidos_enroll":
        result = await eidos.enroll_speaker(
            speaker_id=speaker_id,
            audio_bytes=audio_bytes,
            filename=file.filename or "enroll.wav",
            content_type=file.content_type or "audio/wav",
        )
    elif model == "eidos_verify":
        result = await eidos.verify_speaker(
            speaker_id=speaker_id,
            audio_bytes=audio_bytes,
            filename=file.filename or "verify.wav",
            content_type=file.content_type or "audio/wav",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model. Choose: aletheia_detect, eidos_enroll, eidos_verify",
        )

    return {
        "success": not result.get("error", False),
        "model": model,
        "is_live_api": result.get("is_live_api", False),
        "latency_ms": result.get("latency_ms"),
        "result": result,
    }
