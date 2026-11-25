"""
TRUVEX Employee Management & Voice Enrollment Routes.
Owner: Rounit / Anany
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth_utils import hash_password
from backend.database import get_db
from backend.models import AuditLog, Company, Employee, User
from backend.routes.auth import get_current_user
from backend.schemas import EmployeeCreateRequest, EmployeeResponse
from backend.services.eidos import EidosClient

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registers an employee under the enterprise with automatic Employee ID generation."""
    company_id = current_user.company_id
    if current_user.role == "superadmin":
        # Superadmin can manage any company
        company = db.query(Company).filter(Company.status == "approved").first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No approved enterprise available.",
            )
        company_id = company.id
    elif not company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an enterprise.",
        )

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company or company.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot register employees until the enterprise has been approved by the platform.",
        )

    # Check duplicate email
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An employee with this email already exists.",
        )
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user account with this email already exists.",
        )

    # Generate sequential Employee ID: TRX-E-0001
    total_employees = db.query(Employee).count() + 1
    employee_code = f"TRX-E-{total_employees:04d}"
    speaker_id = f"trx_spk_{employee_code}"

    new_emp = Employee(
        employee_code=employee_code,
        company_id=company.id,
        full_name=payload.full_name,
        email=payload.email,
        department=payload.department,
        designation=payload.designation,
        communication_permissions=payload.communication_permissions,
        can_initiate_calls=payload.can_initiate_calls,
        status="active",
        speaker_id=speaker_id,
        voice_enrolled=False,
        voice_samples_count=0,
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    # Create employee user login
    emp_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="employee",
        company_id=company.id,
        is_active=True,
    )
    db.add(emp_user)

    audit = AuditLog(
        event_type="EMPLOYEE_REGISTERED",
        actor=current_user.email,
        details=f"Employee '{payload.full_name}' registered as {employee_code} in '{company.name}'.",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "employee_id": new_emp.id,
        "employee_code": new_emp.employee_code,
        "speaker_id": new_emp.speaker_id,
        "message": f"Employee registered as {new_emp.employee_code}. Voice biometric enrollment pending.",
    }


@router.get("", response_model=List[dict])
async def list_employees(
    company_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists employees within the enterprise."""
    target_comp_id = company_id or current_user.company_id
    query = db.query(Employee)
    if target_comp_id:
        query = query.filter(Employee.company_id == target_comp_id)
    elif current_user.role != "superadmin":
        return []

    employees = query.order_by(Employee.created_at.desc()).all()
    results = []
    for emp in employees:
        comp = db.query(Company).filter(Company.id == emp.company_id).first()
        results.append(
            {
                "id": emp.id,
                "employee_code": emp.employee_code,
                "company_id": emp.company_id,
                "company_name": comp.name if comp else None,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department,
                "designation": emp.designation,
                "communication_permissions": emp.communication_permissions,
                "can_initiate_calls": emp.can_initiate_calls,
                "status": emp.status,
                "speaker_id": emp.speaker_id,
                "voice_enrolled": emp.voice_enrolled,
                "voice_samples_count": emp.voice_samples_count,
                "created_at": emp.created_at.isoformat() if emp.created_at else None,
            }
        )
    return results


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
):
    """Fetches employee profile by UUID or employee_code."""
    emp = (
        db.query(Employee)
        .filter((Employee.id == employee_id) | (Employee.employee_code == employee_id))
        .first()
    )
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

    comp = db.query(Company).filter(Company.id == emp.company_id).first()
    return {
        "id": emp.id,
        "employee_code": emp.employee_code,
        "company_id": emp.company_id,
        "company_code": comp.company_code if comp else None,
        "company_name": comp.name if comp else None,
        "full_name": emp.full_name,
        "email": emp.email,
        "department": emp.department,
        "designation": emp.designation,
        "communication_permissions": emp.communication_permissions,
        "can_initiate_calls": emp.can_initiate_calls,
        "status": emp.status,
        "speaker_id": emp.speaker_id,
        "voice_enrolled": emp.voice_enrolled,
        "voice_samples_count": emp.voice_samples_count,
    }


@router.post("/{employee_id}/enroll-voice")
async def enroll_employee_voice(
    employee_id: str,
    consent: bool = Form(True),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enrolls an employee's voice sample with DetectifAI Eidos."""
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biometric voice enrollment requires explicit employee consent.",
        )

    emp = (
        db.query(Employee)
        .filter((Employee.id == employee_id) | (Employee.employee_code == employee_id))
        .first()
    )
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

    audio_bytes = await file.read()
    if len(audio_bytes) < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio recording file is empty or corrupted.",
        )

    eidos_client = EidosClient()
    enroll_result = await eidos_client.enroll_speaker(
        speaker_id=emp.speaker_id,
        audio_bytes=audio_bytes,
        display_name=emp.full_name,
        filename=file.filename or "enrollment.wav",
        content_type=file.content_type or "audio/wav",
    )

    if enroll_result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DetectifAI Eidos Enrollment Error: {enroll_result.get('message')}",
        )

    emp.voice_enrolled = True
    emp.voice_samples_count += 1
    db.commit()

    audit = AuditLog(
        event_type="VOICE_ENROLLED",
        actor=current_user.email,
        details=f"Voice sample enrolled for {emp.full_name} ({emp.employee_code}). Live API: {enroll_result.get('is_live_api', False)}",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "employee_code": emp.employee_code,
        "speaker_id": emp.speaker_id,
        "voice_enrolled": True,
        "voice_samples_count": emp.voice_samples_count,
        "enrollment_details": enroll_result,
        "message": "Biometric voice sample enrolled successfully with DetectifAI Eidos.",
    }
