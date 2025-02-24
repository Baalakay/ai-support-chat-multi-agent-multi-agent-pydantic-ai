"""Main application module."""
import logfire
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ai_support_agent.core.config import settings
from ai_support_agent.routers.admin import router as admin_router
from ai_support_agent.routers.ai_query_analysis import router as analysis_router
from ai_support_agent.routers.pdf import router as pdf_router
from ai_support_agent.routers.chat import chat_router, compare_router
from .core.tasks import background_tasks

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Handle application startup and shutdown events."""
    # Startup
    print("Starting up PDF RAG Chatbot")  # Using print instead of logfire
    await background_tasks.start()
    yield
    # Shutdown
    print("Shutting down PDF RAG Chatbot")  # Using print instead of logfire
    await background_tasks.stop()

# Create FastAPI app
app = FastAPI(
    title="PDF RAG Chatbot",
    description="A chatbot that answers questions based on PDF content using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Add more allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(pdf_router)
app.include_router(chat_router)
app.include_router(compare_router)
app.include_router(analysis_router)
app.include_router(admin_router)

@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint to verify the API is running."""
    return JSONResponse(
        content={"message": "PDF RAG Chatbot API is running"},
        status_code=200
    )

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    print("Starting up PDF RAG Chatbot")  # Using print instead of logfire
    await background_tasks.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks."""
    print("Shutting down PDF RAG Chatbot")  # Using print instead of logfire
    await background_tasks.stop()
