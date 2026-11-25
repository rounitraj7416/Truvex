"""
TRUVEX SQLAlchemy Database Models.
Owner: Rounit
Status: Phase 1 Skeleton
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


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User account model for Enterprise Admins and Platform Admins."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="enterprise_admin")  # superadmin, enterprise_admin, employee
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Company(Base):
    """Registered Organization model."""

    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), nullable=False)
    registration_number = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending, approved, suspended
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    employees = relationship("Employee", back_populates="company")


class Employee(Base):
    """Authorized Enterprise Employee."""

    __tablename__ = "employees"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    employee_code = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    speaker_id = Column(String(64), unique=True, index=True, nullable=False)
    voice_enrolled = Column(Boolean, default=False)
    can_initiate_calls = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, suspended

    company = relationship("Company", back_populates="employees")
    sessions = relationship("TrustSession", back_populates="employee")


class TrustSession(Base):
    """Ephemeral Communication Trust ID Session."""

    __tablename__ = "trust_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trust_id = Column(String(20), unique=True, index=True, nullable=False)  # TRX-XXXX-XXXX
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    customer_ref = Column(String(100), nullable=True)
    call_topic = Column(String(255), nullable=False)
    trust_score = Column(Float, nullable=False)
    aletheia_verdict = Column(String(20), nullable=True)  # real, fake
    aletheia_score = Column(Float, nullable=True)
    eidos_decision = Column(String(20), nullable=True)  # match, no_match
    eidos_similarity = Column(Float, nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, EXPIRED, REVOKED, COMPLETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    employee = relationship("Employee", back_populates="sessions")


class FraudReport(Base):
    """Customer reported fraud/suspicious calls."""

    __tablename__ = "fraud_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claimed_trust_id = Column(String(20), nullable=True, index=True)
    claimed_company = Column(String(255), nullable=True)
    caller_phone = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
