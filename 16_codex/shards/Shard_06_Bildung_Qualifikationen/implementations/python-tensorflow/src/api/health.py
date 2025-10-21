"""Health check endpoints"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/live")
async def liveness():
    """Liveness probe"""
    return {"status": "alive"}

@router.get("/ready")
async def readiness():
    """Readiness probe - check dependencies"""
    # TODO: Check Redis, Audit Logging, etc.
    dependencies = {
        "redis": "up",
        "audit_logging": "up"
    }
    
    all_up = all(v == "up" for v in dependencies.values())
    status_code = 200 if all_up else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_up else "not_ready",
            "dependencies": dependencies
        }
    )
