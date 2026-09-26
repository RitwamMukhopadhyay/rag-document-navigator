from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Pharma Research & Intelligence Agent",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
