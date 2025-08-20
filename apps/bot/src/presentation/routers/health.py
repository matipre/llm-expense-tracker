"""
Health check router for the Bot Service.
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "bot",
        "timestamp": datetime.utcnow().isoformat(),
    }
