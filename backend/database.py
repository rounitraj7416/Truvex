"""
TRUVEX Database Connection & Initialization Module.
Owner: Rounit / Anany
"""

from datetime import datetime, timezone
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./truvex.db")

# Render uses 'postgres://' but SQLAlchemy 2.x requires 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to retrieve database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes tables and seeds baseline demonstration entities if empty."""
    from backend.auth_utils import hash_password
    from backend.models import Company, Employee, User

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Superadmin User
        superadmin = db.query(User).filter(User.role == "superadmin").first()
        if not superadmin:
            admin_user = User(
                email="admin@truvex.ai",
                hashed_password=hash_password("AdminPass123!"),
                full_name="TRUVEX Platform Administrator",
                role="superadmin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()

        # 2. Demo Company (Apex Global Bank - Pre-Approved)
        demo_company = db.query(Company).filter(Company.company_code == "TRX-C-0001").first()
        if not demo_company:
            demo_company = Company(
                company_code="TRX-C-0001",
                name="Apex Global Bank",
                industry="Banking & Financial Services",
                official_email="security@apexbank.example",
                official_website="https://apexbank.example",
                registration_number="REG-IN-2026-0912",
                support_contact="+1-800-APEX-SEC",
                declared_employees=250,
                status="approved",
            )
            db.add(demo_company)
            db.commit()
            db.refresh(demo_company)

            # Enterprise Admin for Apex Bank
            corp_admin = User(
                email="admin@apexbank.example",
                hashed_password=hash_password("ApexBank123!"),
                full_name="Sarah Connor (Security Dir)",
                role="enterprise_admin",
                company_id=demo_company.id,
                is_active=True,
            )
            db.add(corp_admin)
            db.commit()

            # Demo Employee (Marcus Vance - Active & Voice Enrolled)
            demo_emp = Employee(
                employee_code="TRX-E-0001",
                company_id=demo_company.id,
                full_name="Marcus Vance",
                email="marcus@apexbank.example",
                department="Fraud Prevention Operations",
                designation="Senior Fraud Analyst",
                communication_permissions="fraud_alerts,account_verification,urgent_security",
                can_initiate_calls=True,
                status="active",
                speaker_id="trx_spk_TRX-E-0001",
                voice_enrolled=True,
                voice_samples_count=2,
            )
            db.add(demo_emp)

            # User account for Marcus
            emp_user = User(
                email="marcus@apexbank.example",
                hashed_password=hash_password("Marcus123!"),
                full_name="Marcus Vance",
                role="employee",
                company_id=demo_company.id,
                is_active=True,
            )
            db.add(emp_user)
            db.commit()

    finally:
        db.close()
