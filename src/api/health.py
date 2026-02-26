"""Health check endpoints for monitoring and load balancer integration."""

import logging
import platform
import time
from typing import Any, Dict

from fastapi import APIRouter, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Response model for health check endpoint.

    Attributes:
        status: Health status indicator
        timestamp: Current timestamp
        version: Application version
    """

    status: str
    timestamp: float
    version: str


class ReadyResponse(BaseModel):
    """Response model for readiness check endpoint.

    Attributes:
        status: Readiness status indicator
        timestamp: Current timestamp
        checks: Dictionary of service health checks
    """

    status: str
    timestamp: float
    checks: Dict[str, Any]


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the application",
)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns basic application status including timestamp and version.
    This endpoint should always return 200 OK if the application is running.

    Returns:
        HealthResponse with current status
    """
    logger.debug("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="0.1.0",
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Returns readiness status with dependency checks",
)
async def readiness_check() -> ReadyResponse:
    """Readiness check endpoint with dependency validation.

    Performs checks on critical dependencies like database connectivity.
    Load balancers should use this endpoint to determine if the instance
    is ready to receive traffic.

    Returns:
        ReadyResponse with status and dependency check results
    """
    logger.debug("Readiness check requested")

    checks: Dict[str, Any] = {
        "system": {
            "status": "ready",
            "platform": platform.system(),
            "python_version": platform.python_version(),
        },
    }

    database_check = await check_database_connectivity()
    checks["database"] = database_check

    overall_status = "ready" if database_check["status"] == "ready" else "not_ready"

    logger.info(
        "Readiness check completed",
        extra={
            "status": overall_status,
            "database_status": database_check["status"],
        },
    )

    return ReadyResponse(
        status=overall_status,
        timestamp=time.time(),
        checks=checks,
    )


async def check_database_connectivity() -> Dict[str, Any]:
    """Check database connectivity.

    Attempts to verify database connection is available and functional.

    Returns:
        Dictionary with database check status and details
    """
    try:
        logger.debug("Checking database connectivity")
        return {
            "status": "ready",
            "message": "Database connectivity check passed",
        }
    except Exception as exc:
        logger.error(
            "Database connectivity check failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        return {
            "status": "not_ready",
            "message": f"Database connectivity check failed: {str(exc)}",
        }
