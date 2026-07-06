"""
QR Code Generator - FastAPI Backend
Main application entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .api.v1.router import api_router
from .core.logger import setup_logger

# Initialize logger
logger = logging.getLogger(__name__)

# Load application settings
settings = get_settings()

# Setup application logger
setup_logger(settings)


def create_app() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title=settings.api_title,
        description=settings.app_description,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint to verify the API is running."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "docs": settings.docs_url,
            "health": "/health",
        }

    logger.info(f"✅ {settings.app_name} v{settings.app_version} started successfully")
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
        workers=settings.server_workers,
        log_level="info",
    )
