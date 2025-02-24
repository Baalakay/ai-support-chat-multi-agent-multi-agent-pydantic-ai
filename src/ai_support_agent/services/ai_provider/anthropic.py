"""Anthropic provider implementation."""

from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
import anthropic
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr
from pydantic_ai import Agent, RunContext

from .base import BaseLLMProvider, LLMResponse, LLMConfig
from ...types.agent import AgentDependencies
from ...config.config import get_settings


class AnthropicMetrics(BaseModel):
    """Anthropic-specific metrics."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "total_api_calls": 150,
                    "total_api_errors": 2,
                    "average_response_time": 200.5,
                    "total_cost": 0.015
                }
            ]
        }
    )
    
    total_api_calls: int = Field(default=0, description="Total number of API calls")
    total_api_errors: int = Field(default=0, description="Total number of API errors")
    average_response_time: float = Field(default=0.0, description="Average API response time in ms")
    total_cost: float = Field(default=0.0, description="Estimated total cost in USD")
    _raw_metrics: Dict[str, Any] = PrivateAttr(default_factory=dict)
    
    @computed_field
    @property
    def error_rate(self) -> float:
        """Calculate API error rate."""
        return self.total_api_errors / self.total_api_calls if self.total_api_calls > 0 else 0.0


class AnthropicProvider(BaseLLMProvider):
    """Anthropic implementation of LLM provider."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid"
    )
    
    config: LLMConfig = Field(..., description="Anthropic configuration")
    _anthropic_metrics: AnthropicMetrics = PrivateAttr(default_factory=AnthropicMetrics)
    _response_times: List[float] = PrivateAttr(default_factory=list)
    _last_api_call: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    
    def __init__(self, **data: Any):
        """Initialize Anthropic client."""
        super().__init__(**data)
        settings = get_settings()
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )
    
    @Agent.tool
    async def complete(
        self,
        prompt: str,
        context: RunContext[AgentDependencies]
    ) -> LLMResponse:
        """Generate text completion using Anthropic.
        
        Args:
            prompt: The prompt to complete
            context: Runtime context with dependencies
            
        Returns:
            Standardized response with generated text
            
        Raises:
            anthropic.APIError: If API request fails
        """
        try:
            start_time = datetime.now(UTC)
            
            response = await self.client.messages.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            end_time = datetime.now(UTC)
            latency = (end_time - start_time).total_seconds() * 1000
            
            # Estimate token usage since Anthropic doesn't provide it directly
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
            completion_tokens = len(response.content[0].text.split()) * 1.3
            total_tokens = int(prompt_tokens + completion_tokens)
            
            usage = {
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": total_tokens
            }
            
            # Update metrics
            self._update_metrics("completion", total_tokens, latency)
            self._update_anthropic_metrics(True, latency, total_tokens)
            
            return LLMResponse(
                text=response.content[0].text,
                usage=usage,
                model=response.model,
                metadata={
                    "finish_reason": response.stop_reason,
                    "latency_ms": latency
                }
            )
            
        except anthropic.APIError as e:
            self._update_anthropic_metrics(False, 0, 0)
            raise
    
    @Agent.tool
    async def get_embedding(
        self,
        text: str,
        context: RunContext[AgentDependencies]
    ) -> list[float]:
        """Get embedding vector using Anthropic.
        
        Args:
            text: Text to get embedding for
            context: Runtime context with dependencies
            
        Raises:
            NotImplementedError: Anthropic does not currently support embeddings
        """
        raise NotImplementedError("Anthropic does not currently support embeddings")
    
    def _update_anthropic_metrics(
        self,
        success: bool,
        latency: float,
        tokens: int
    ) -> None:
        """Update Anthropic-specific metrics.
        
        Args:
            success: Whether API call was successful
            latency: API response time in milliseconds
            tokens: Number of tokens used
        """
        self._anthropic_metrics.total_api_calls += 1
        if not success:
            self._anthropic_metrics.total_api_errors += 1
            
        # Update response time average
        self._response_times.append(latency)
        if len(self._response_times) > 100:  # Keep last 100 calls
            self._response_times.pop(0)
        self._anthropic_metrics.average_response_time = (
            sum(self._response_times) / len(self._response_times)
        )
        
        # Update cost (rough estimate)
        # Claude: $0.015 per 1K tokens
        cost_per_token = 0.015 / 1000
        self._anthropic_metrics.total_cost += tokens * cost_per_token
        
        # Update last API call info
        self._last_api_call = {
            "success": success,
            "latency": latency,
            "tokens": tokens,
            "timestamp": datetime.now(UTC)
        }
    
    @property
    def anthropic_metrics(self) -> AnthropicMetrics:
        """Get Anthropic-specific metrics."""
        return self._anthropic_metrics
    
    @property
    def last_api_call(self) -> Optional[Dict[str, Any]]:
        """Get information about last API call."""
        return self._last_api_call 