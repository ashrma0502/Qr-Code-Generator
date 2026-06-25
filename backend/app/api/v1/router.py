"""
API v1 router.
Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints.qr import router as qr_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(qr_router)
