"""
TRUVEX Company Management Routes.
Owner: Rounit
Status: Phase 1 Placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/status")
async def company_status():
    return {"message": "Companies router initialized."}
