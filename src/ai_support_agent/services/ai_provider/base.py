"""Base LLM provider implementation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from ...types.agent import AgentDependencies


class LLMResponse(BaseModel):
    """Response from LLM provider."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    text: str = Field(..., description="Generated text")
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Response metadata"
    )


class BaseLLMProvider(Agent[AgentDependencies]):
    """Base class for LLM providers."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid"
    )
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Base LLM provider focused on:
        1. Generating high-quality responses
        2. Maintaining consistent output
        3. Handling errors gracefully""" 