"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.health import router as health_router
from src.core.config import Settings
from src.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    logger.info("Application startup initiated", extra={"event": "startup"})
    yield
    logger.info("Application shutdown initiated", extra={"event": "shutdown"})


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance.

    Returns:
        Configured FastAPI application
    """
    settings = Settings()
    setup_logging(debug=settings.DEBUG)

    app = FastAPI(
        title="Resume API",
        description="API for resume and cover letter generation",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    configure_cors(app, settings)
    configure_middleware(app)
    configure_routes(app)
    configure_exception_handlers(app)

    return app


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS middleware.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(
        "CORS configured",
        extra={
            "allowed_origins": settings.CORS_ORIGINS,
        },
    )


def configure_middleware(app: FastAPI) -> None:
    """Configure application middleware.

    Args:
        app: FastAPI application instance
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming HTTP requests with context.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else None,
            },
        )
        try:
            response = await call_next(request)
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                },
            )
            return response
        except Exception as exc:
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise


def configure_routes(app: FastAPI) -> None:
    """Configure application routes.

    Args:
        app: FastAPI application instance
    """
    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router, tags=["authentication"])
    logger.info("Routes configured")


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors.

        Args:
            request: Incoming HTTP request
            exc: Validation error exception

        Returns:
            JSON response with error details
        """
        logger.warning(
            "Validation error",
            extra={
                "path": request.url.path,
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "body": exc.body,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general uncaught exceptions.

        Args:
            request: Incoming HTTP request
            exc: Exception that was raised

        Returns:
            JSON response with error details
        """
        logger.error(
            "Unhandled exception",
            extra={
                "path": request.url.path,
                "error": str(exc),
            },
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
            },
        )

    logger.info("Exception handlers configured")


app = create_app()
