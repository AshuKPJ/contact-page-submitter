from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware"""
    # Debug: Print what origins we're using
    origins = settings.CORS_ORIGINS
    print(f"[CORS] Setting up CORS with origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Temporarily allow all origins for debugging
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
