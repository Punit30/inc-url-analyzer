from fastapi import APIRouter

from app.api.v1.routes import url, profiles

api_router = APIRouter()

# Include all route modules
api_router.include_router(url.router, prefix="/url", tags=["URL"])
api_router.include_router(profiles.router, prefix="/profile", tags=["Profile"])
