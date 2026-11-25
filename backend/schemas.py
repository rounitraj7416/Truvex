"""
TRUVEX Pydantic Validation Schemas.
Owner: Rounit / Anany
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


# Base
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


# Auth
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 7200
    user: Dict[str, Any]


# Company Registration
class CompanyRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    industry: str = Field(..., max_length=100)
    official_email: EmailStr
    official_website: str = Field(..., max_length=255)
    registration_number: str = Field(..., max_length=100)
    support_contact: str = Field(..., max_length=100)
    declared_employees: int = Field(default=1, ge=1)
    admin_name: str = Field(..., min_length=2, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)


class CompanyStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected|suspended)$")
    reason: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    company_code: Optional[str]
    name: str
    industry: str
    official_email: str
    official_website: str
    registration_number: str
    support_contact: str
    declared_employees: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Employee
class EmployeeCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    department: str = Field(..., max_length=100)
    designation: str = Field(..., max_length=100)
    communication_permissions: str = "fraud_alerts,account_verification,general_support"
    can_initiate_calls: bool = True


class EmployeeResponse(BaseModel):
    id: str
    employee_code: Optional[str]
    company_id: str
    full_name: str
    email: str
    department: str
    designation: str
    communication_permissions: str
    can_initiate_calls: bool
    status: str
    speaker_id: str
    voice_enrolled: bool
    voice_samples_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Session Verification & Trust ID
class PreCallVerifyRequest(BaseModel):
    employee_id: str
    customer_ref: str = Field(..., min_length=3, max_length=100)
    call_topic: str = Field(..., min_length=3, max_length=255)
    communication_category: str = "fraud_prevention"
    consent_given: bool = True


class SessionResponse(BaseModel):
    success: bool
    session_id: str  # TRX-S-849201
    trust_id: str  # same as session_id
    trust_score: float
    verdict: str  # VERIFIED, UNVERIFIED, MANUAL_REVIEW
    challenge_code: str
    expires_at: str
    expires_in_seconds: int
    layer_results: Dict[str, Any]
    ai_evidence: Dict[str, Any]


# Customer Lookup
class CustomerLookupRequest(BaseModel):
    company_id_or_code: Optional[str] = ""
    employee_id_or_code: Optional[str] = ""
    session_id: str


class CustomerLookupResponse(BaseModel):
    valid: bool
    session_id: str
    company_name: Optional[str] = None
    company_code: Optional[str] = None
    company_approved: bool = False
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    call_topic: Optional[str] = None
    communication_category: Optional[str] = None
    voice_authenticity: Dict[str, Any]
    speaker_verification: Dict[str, Any]
    authority_verification: bool
    session_valid: bool
    status: str
    trust_score: float
    overall_verdict: str
    challenge_code: Optional[str] = None
    remaining_seconds: int
    expires_at: str


class ChallengeConfirmRequest(BaseModel):
    session_id: str
    challenge_code: str


# Fraud Report
class FraudReportCreate(BaseModel):
    claimed_company_id: Optional[str] = None
    claimed_employee_id: Optional[str] = None
    claimed_session_id: Optional[str] = None
    claimed_company_name: Optional[str] = None
    caller_phone: Optional[str] = None
    description: str = Field(..., min_length=5)
    severity: str = "medium"


# Platform Stats
class PlatformStatsResponse(BaseModel):
    total_companies: int
    approved_companies: int
    pending_companies: int
    total_employees: int
    voice_enrolled_employees: int
    active_sessions: int
    expired_sessions: int
    total_fraud_reports: int
    detectif_configured: bool
    detectif_mock_fallback: bool


# Phone Lookup
class PhoneLookupRequest(BaseModel):
    country_code: str = "+1"
    phone_number: str = Field(..., min_length=3, max_length=30)


class PhoneLookupResponse(BaseModel):
    status: str  # REGISTERED_BUSINESS, UNREGISTERED, ACTIVE_SESSION_FOUND, SUSPICIOUS_FLAGGED, UNAVAILABLE
    phone_number: str
    formatted_phone: str
    is_registered_business: bool
    company_name: Optional[str] = None
    company_code: Optional[str] = None
    company_industry: Optional[str] = None
    active_sessions_count: int = 0
    fraud_reports_count: int = 0
    security_notice: str

