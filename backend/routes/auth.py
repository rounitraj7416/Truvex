"""
TRUVEX Authentication & Authorization Routes.
Owner: Rounit
Status: Phase 1 Placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/status")
async def auth_status():
    return {"message": "Auth router initialized."}
