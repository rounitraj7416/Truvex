"""
TRUVEX Session Verification & Trust ID Routes.
Owner: Rounit / Anany
Status: Phase 1 Placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/status")
async def verification_status():
    return {"message": "Verification router initialized."}
