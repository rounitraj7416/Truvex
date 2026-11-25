"""
TRUVEX Platform Administration Routes.
Owner: Rounit
Status: Phase 1 Placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/status")
async def admin_status():
    return {"message": "Admin router initialized."}
