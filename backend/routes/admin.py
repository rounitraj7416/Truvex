"""
TRUVEX Platform Administration & Control Panel Routes.
Owner: Rounit / Anany
"""

from datetime import datetime, timezone
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import AuditLog, Company, Employee, FraudReport, TrustSession, User
from backend.routes.auth import get_current_user
from backend.schemas import PlatformStatsResponse

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(
    db: Session = Depends(get_db),
):
    """Aggregates platform security statistics and DetectifAI integration health."""
    total_companies = db.query(Company).count()
    approved_companies = db.query(Company).filter(Company.status == "approved").count()
    pending_companies = db.query(Company).filter(Company.status == "pending").count()

    total_employees = db.query(Employee).count()
    voice_enrolled = db.query(Employee).filter(Employee.voice_enrolled == True).count()

    now_utc = datetime.now(timezone.utc)
    active_sessions = (
        db.query(TrustSession)
        .filter(TrustSession.status == "ACTIVE", TrustSession.expires_at > now_utc)
        .count()
    )
    expired_sessions = (
        db.query(TrustSession)
        .filter((TrustSession.status != "ACTIVE") | (TrustSession.expires_at <= now_utc))
        .count()
    )
    total_reports = db.query(FraudReport).count()

    detectif_key = os.getenv("DETECTIF_API_KEY", "")
    has_real_key = bool(detectif_key and not detectif_key.startswith("dtf_live_your_"))
    mock_fallback = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower() == "true"

    return PlatformStatsResponse(
        total_companies=total_companies,
        approved_companies=approved_companies,
        pending_companies=pending_companies,
        total_employees=total_employees,
        voice_enrolled_employees=voice_enrolled,
        active_sessions=active_sessions,
        expired_sessions=expired_sessions,
        total_fraud_reports=total_reports,
        detectif_configured=has_real_key,
        detectif_mock_fallback=mock_fallback,
    )


@router.get("/fraud-reports")
async def get_fraud_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves fraud reports (restricted to platform superadmin or enterprise admin)."""
    reports = db.query(FraudReport).order_by(FraudReport.created_at.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "claimed_company_name": r.claimed_company_name,
            "claimed_session_id": r.claimed_session_id,
            "caller_phone": r.caller_phone,
            "description": r.description,
            "severity": r.severity,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.get("/audit-logs")
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves immutable security audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "actor": l.actor,
            "details": l.details,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
