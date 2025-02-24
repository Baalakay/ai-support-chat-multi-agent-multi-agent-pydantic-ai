"""Admin routes for managing system state."""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ...services.agent_service import AgentService
from ..dependencies import get_agent_service


router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Remove all cache-related endpoints and models 