"""
TRUVEX SQLAlchemy Database Models.
Owner: Rounit / Anany
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Company(Base):
    """Registered Organization model."""

    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_code = Column(String(20), unique=True, index=True, nullable=True)  # TRX-C-0001
    name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100), nullable=False)
    official_email = Column(String(255), nullable=False)
    official_website = Column(String(255), nullable=False)
    registration_number = Column(String(100), nullable=False)
    support_contact = Column(String(100), nullable=False)
    declared_employees = Column(Integer, default=1)
    status = Column(String(50), default="pending")  # pending, approved, rejected, suspended
    rejection_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    sessions = relationship("TrustSession", back_populates="company")


class User(Base):
    """User account model for Admins and Employees."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="enterprise_admin")  # superadmin, enterprise_admin, employee
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="users")


class Employee(Base):
    """Authorized Enterprise Employee."""

    __tablename__ = "employees"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_code = Column(String(20), unique=True, index=True, nullable=True)  # TRX-E-0001
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    communication_permissions = Column(String(255), default="fraud_alerts,account_verification,general_support")
    can_initiate_calls = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, suspended, terminated
    speaker_id = Column(String(64), unique=True, index=True, nullable=False)  # trx_spk_TRX-E-0001
    voice_enrolled = Column(Boolean, default=False)
    voice_samples_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="employees")
    sessions = relationship("TrustSession", back_populates="employee")


class TrustSession(Base):
    """Ephemeral Communication Trust ID Session."""

    __tablename__ = "trust_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(24), unique=True, index=True, nullable=False)  # TRX-S-849201 or TRX-XXXX-XXXX
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    customer_ref = Column(String(100), nullable=False)  # e.g. CUST-9021 or +91-***-9921
    call_topic = Column(String(255), nullable=False)
    communication_category = Column(String(100), default="fraud_prevention")
    
    # Layer Results & AI Evidence
    trust_score = Column(Float, nullable=False, default=0.0)
    aletheia_verdict = Column(String(20), nullable=True)  # real, fake, mock
    aletheia_score = Column(Float, nullable=True)
    eidos_decision = Column(String(20), nullable=True)  # match, no_match, mock
    eidos_similarity = Column(Float, nullable=True)
    overall_verdict = Column(String(50), default="VERIFIED")  # VERIFIED, UNVERIFIED, MANUAL_REVIEW, REJECTED

    # Challenge-Response
    challenge_code = Column(String(6), nullable=False)  # e.g. 4-digit code "4928"
    challenge_confirmed = Column(Boolean, default=False)

    status = Column(String(50), default="ACTIVE")  # ACTIVE, EXPIRED, REVOKED, COMPLETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    company = relationship("Company", back_populates="sessions")
    employee = relationship("Employee", back_populates="sessions")


class FraudReport(Base):
    """Customer reported fraud/suspicious calls."""

    __tablename__ = "fraud_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claimed_company_id = Column(String(50), nullable=True)
    claimed_employee_id = Column(String(50), nullable=True)
    claimed_session_id = Column(String(50), nullable=True, index=True)
    claimed_company_name = Column(String(255), nullable=True)
    caller_phone = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="new")  # new, investigating, resolved
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    """Platform-wide security and event audit log."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), nullable=False, index=True)
    actor = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
