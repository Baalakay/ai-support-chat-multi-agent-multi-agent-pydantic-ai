"""FastAPI application setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.config import get_settings
from .routes import router

# Create FastAPI app
app = FastAPI(
    title="AI Support Agent",
    description="AI-powered PDF analysis and comparison agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(router) 