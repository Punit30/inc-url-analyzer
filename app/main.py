from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.api import api_router
from app.core.configs import settings
from app.core.session import init_db
from app.core.seed_db import seed_all
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()

    # logic to fake db data
    # if os.environ.get("ENV") == "local":
    #     seed_all()

    yield
    # Shutdown logic (optional)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root URL to API documentation"""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/health", tags=["health"], include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": settings.VERSION}
