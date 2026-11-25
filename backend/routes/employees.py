"""
TRUVEX Employee Management & Voice Enrollment Routes.
Owner: Rounit
Status: Phase 1 Placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/status")
async def employee_status():
    return {"message": "Employees router initialized."}
