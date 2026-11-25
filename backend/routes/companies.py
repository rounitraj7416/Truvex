"""
TRUVEX Company Registration and Administrative Management Routes.
Owner: Rounit / Anany
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth_utils import hash_password
from backend.database import get_db
from backend.models import AuditLog, Company, Employee, User
from backend.routes.auth import get_current_user
from backend.schemas import CompanyRegisterRequest, CompanyResponse, CompanyStatusUpdate

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_company(payload: CompanyRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new company with pending platform accreditation and sets up initial admin."""
    # Check duplicate company name or email
    if db.query(Company).filter(Company.name == payload.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A company with this legal name is already registered.",
        )
    if db.query(User).filter(User.email == payload.admin_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this administrator email already exists.",
        )

    # Create company record (status: pending)
    new_company = Company(
        name=payload.name,
        industry=payload.industry,
        official_email=payload.official_email,
        official_website=payload.official_website,
        registration_number=payload.registration_number,
        support_contact=payload.support_contact,
        declared_employees=payload.declared_employees,
        status="pending",
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    # Create initial enterprise administrator
    admin_user = User(
        email=payload.admin_email,
        hashed_password=hash_password(payload.admin_password),
        full_name=payload.admin_name,
        role="enterprise_admin",
        company_id=new_company.id,
        is_active=True,
    )
    db.add(admin_user)

    # Audit log
    audit = AuditLog(
        event_type="COMPANY_REGISTERED",
        actor=payload.admin_email,
        details=f"Company '{payload.name}' submitted registration for accreditation.",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "message": "Company registered successfully. Pending platform administrator accreditation.",
        "company_id": new_company.id,
        "status": new_company.status,
    }


@router.get("", response_model=List[dict])
async def list_companies(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Lists companies with employee statistics (public or filtered)."""
    query = db.query(Company)
    if status_filter:
        query = query.filter(Company.status == status_filter)
    companies = query.order_by(Company.created_at.desc()).all()

    results = []
    for comp in companies:
        registered_count = db.query(Employee).filter(Employee.company_id == comp.id).count()
        enrolled_count = (
            db.query(Employee)
            .filter(Employee.company_id == comp.id, Employee.voice_enrolled == True)
            .count()
        )
        results.append(
            {
                "id": comp.id,
                "company_code": comp.company_code,
                "name": comp.name,
                "industry": comp.industry,
                "official_email": comp.official_email,
                "official_website": comp.official_website,
                "registration_number": comp.registration_number,
                "support_contact": comp.support_contact,
                "declared_employees": comp.declared_employees,
                "registered_employees": registered_count,
                "voice_enrolled_employees": enrolled_count,
                "status": comp.status,
                "rejection_reason": comp.rejection_reason,
                "created_at": comp.created_at.isoformat() if comp.created_at else None,
            }
        )
    return results


@router.get("/{company_id}")
async def get_company(company_id: str, db: Session = Depends(get_db)):
    """Retrieves specific company details."""
    comp = (
        db.query(Company)
        .filter((Company.id == company_id) | (Company.company_code == company_id))
        .first()
    )
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    registered_count = db.query(Employee).filter(Employee.company_id == comp.id).count()
    enrolled_count = (
        db.query(Employee)
        .filter(Employee.company_id == comp.id, Employee.voice_enrolled == True)
        .count()
    )

    return {
        "id": comp.id,
        "company_code": comp.company_code,
        "name": comp.name,
        "industry": comp.industry,
        "official_email": comp.official_email,
        "official_website": comp.official_website,
        "registration_number": comp.registration_number,
        "support_contact": comp.support_contact,
        "declared_employees": comp.declared_employees,
        "registered_employees": registered_count,
        "voice_enrolled_employees": enrolled_count,
        "status": comp.status,
        "created_at": comp.created_at.isoformat() if comp.created_at else None,
    }


@router.patch("/{company_id}/status")
async def update_company_status(
    company_id: str,
    payload: CompanyStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allows Superadmins to approve, reject, or suspend a company."""
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform superadministrators can update company accreditation status.",
        )

    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    comp.status = payload.status
    if payload.reason:
        comp.rejection_reason = payload.reason

    # Automatically generate sequential Company ID if approved for the first time
    if payload.status == "approved" and not comp.company_code:
        approved_count = (
            db.query(Company).filter(Company.company_code != None).count() + 1
        )
        comp.company_code = f"TRX-C-{approved_count:04d}"

    audit = AuditLog(
        event_type=f"COMPANY_{payload.status.upper()}",
        actor=current_user.email,
        details=f"Company '{comp.name}' set to {payload.status}. Code: {comp.company_code}",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "company_id": comp.id,
        "company_code": comp.company_code,
        "status": comp.status,
        "message": f"Company status updated to {comp.status}.",
    }
