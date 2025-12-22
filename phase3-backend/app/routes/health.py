"""
Health check endpoints for Phase 3 Backend.

Provides liveness and readiness checks for deployment orchestration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
import httpx

from app.db import get_session
from app.config import settings


router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Liveness probe - checks if the service is running.

    Returns 200 if the application process is alive.
    Used by Railway/Kubernetes to detect if container should be restarted.
    """
    return {"status": "healthy", "service": "phase3-backend"}


@router.get("/readiness")
async def readiness_check(session: AsyncSession = Depends(get_session)):
    """
    Readiness probe - checks if the service is ready to accept traffic.

    Verifies:
    - Database connection is working
    - OpenAI API key is configured
    - MCP server URL is configured

    Returns 200 if ready, 503 if not ready.
    Used by Railway/Kubernetes to determine if traffic should be routed to this instance.
    """
    checks = {"database": False, "openai_configured": False, "mcp_configured": False}

    # Check database connection
    try:
        result = await session.execute(text("SELECT 1"))
        checks["database"] = result.scalar() == 1
    except Exception as e:
        print(f"Database check failed: {e}")
        checks["database"] = False

    # Check OpenAI API key configured
    checks["openai_configured"] = bool(settings.openai_api_key)

    # Check MCP server URL configured
    checks["mcp_configured"] = bool(settings.mcp_server_url)

    # Determine overall readiness
    all_ready = all(checks.values())

    if not all_ready:
        raise HTTPException(status_code=503, detail={"ready": False, "checks": checks})

    return {"ready": True, "checks": checks}
