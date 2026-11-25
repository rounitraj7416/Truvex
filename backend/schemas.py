"""
TRUVEX Pydantic Validation Schemas.
Owner: Rounit
Status: Phase 1 Skeleton
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr, Field


# Base Response
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


# Auth
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: str = "enterprise_admin"
    company_id: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 3600


# Company
class CompanyRegister(BaseModel):
    name: str = Field(..., max_length=255)
    domain: str = Field(..., max_length=255)
    registration_number: str = Field(..., max_length=100)
    industry: Optional[str] = None


class CompanyStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|suspended)$")
    notes: Optional[str] = None


# Employee
class EmployeeCreate(BaseModel):
    company_id: str
    full_name: str
    employee_code: str
    email: EmailStr
    department: str
    can_initiate_calls: bool = True


# Trust Session & Verification
class TrustSessionCreate(BaseModel):
    customer_ref: Optional[str] = None
    call_topic: str


class TrustIdLookupResponse(BaseModel):
    valid: bool
    trust_id: str
    status: str
    company_name: Optional[str] = None
    company_verified: bool = False
    representative_name: Optional[str] = None
    department: Optional[str] = None
    call_topic: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    remaining_seconds: Optional[int] = None
    trust_level: str = "STANDARD"
    audio_checks: Optional[Dict[str, Any]] = None


# Fraud Report
class FraudReportCreate(BaseModel):
    claimed_trust_id: Optional[str] = None
    claimed_company: Optional[str] = None
    caller_phone: Optional[str] = None
    description: str
    severity: str = "medium"
