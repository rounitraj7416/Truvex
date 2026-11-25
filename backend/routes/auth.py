"""
TRUVEX Authentication & User Session Routes.
Owner: Rounit / Anany
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth_utils import create_access_token, decode_access_token, verify_password
from backend.database import get_db
from backend.models import Company, User
from backend.schemas import TokenResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> User:
    """Dependency to validate JWT and extract active user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authentication header.",
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token expired or signature invalid.",
        )
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account disabled or not found.",
        )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticates users (Superadmin, Enterprise Admin, Employee) and issues JWT."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    company_code = None
    company_name = None
    if user.company_id:
        company = db.query(Company).filter(Company.id == user.company_id).first()
        if company:
            company_code = company.company_code
            company_name = company.name

    token = create_access_token(
        {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_seconds": 7200,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "company_id": user.company_id,
            "company_code": company_code,
            "company_name": company_name,
        },
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns profile information for the authenticated user."""
    company_code = None
    company_name = None
    company_status = None
    if current_user.company_id:
        comp = db.query(Company).filter(Company.id == current_user.company_id).first()
        if comp:
            company_code = comp.company_code
            company_name = comp.name
            company_status = comp.status

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "company_id": current_user.company_id,
        "company_code": company_code,
        "company_name": company_name,
        "company_status": company_status,
    }
