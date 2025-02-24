"""OpenAI provider implementation."""

from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr
from pydantic_ai import Agent, RunContext

from .base import BaseLLMProvider, LLMResponse, LLMConfig
from ...types.agent import AgentDependencies
from ...config.config import get_settings


class OpenAIMetrics(BaseModel):
    """OpenAI-specific metrics."""
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


class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation of LLM provider."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid"
    )
    
    config: LLMConfig = Field(..., description="OpenAI configuration")
    _openai_metrics: OpenAIMetrics = PrivateAttr(default_factory=OpenAIMetrics)
    _response_times: List[float] = PrivateAttr(default_factory=list)
    _last_api_call: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    
    def __init__(self, **data: Any):
        """Initialize OpenAI client."""
        super().__init__(**data)
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id
        )
    
    @Agent.tool
    async def complete(
        self,
        prompt: str,
        context: RunContext[AgentDependencies]
    ) -> LLMResponse:
        """Generate text completion using OpenAI.
        
        Args:
            prompt: The prompt to complete
            context: Runtime context with dependencies
            
        Returns:
            Standardized response with generated text
            
        Raises:
            openai.OpenAIError: If API request fails
        """
        try:
            start_time = datetime.now(UTC)
            
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                presence_penalty=self.config.presence_penalty,
                frequency_penalty=self.config.frequency_penalty
            )
            
            end_time = datetime.now(UTC)
            latency = (end_time - start_time).total_seconds() * 1000
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Update metrics
            self._update_metrics("completion", usage["total_tokens"], latency)
            self._update_openai_metrics(True, latency, usage["total_tokens"])
            
            return LLMResponse(
                text=response.choices[0].message.content,
                usage=usage,
                model=response.model,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "latency_ms": latency
                }
            )
            
        except openai.OpenAIError as e:
            self._update_openai_metrics(False, 0, 0)
            raise
    
    @Agent.tool
    async def get_embedding(
        self,
        text: str,
        context: RunContext[AgentDependencies]
    ) -> list[float]:
        """Get embedding vector using OpenAI.
        
        Args:
            text: Text to get embedding for
            context: Runtime context with dependencies
            
        Returns:
            Embedding vector
            
        Raises:
            openai.OpenAIError: If API request fails
        """
        try:
            start_time = datetime.now(UTC)
            
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            end_time = datetime.now(UTC)
            latency = (end_time - start_time).total_seconds() * 1000
            
            # Update metrics
            self._update_metrics("embedding", response.usage.total_tokens, latency)
            self._update_openai_metrics(True, latency, response.usage.total_tokens)
            
            return response.data[0].embedding
            
        except openai.OpenAIError as e:
            self._update_openai_metrics(False, 0, 0)
            raise
    
    def _update_openai_metrics(
        self,
        success: bool,
        latency: float,
        tokens: int
    ) -> None:
        """Update OpenAI-specific metrics.
        
        Args:
            success: Whether API call was successful
            latency: API response time in milliseconds
            tokens: Number of tokens used
        """
        self._openai_metrics.total_api_calls += 1
        if not success:
            self._openai_metrics.total_api_errors += 1
            
        # Update response time average
        self._response_times.append(latency)
        if len(self._response_times) > 100:  # Keep last 100 calls
            self._response_times.pop(0)
        self._openai_metrics.average_response_time = (
            sum(self._response_times) / len(self._response_times)
        )
        
        # Update cost (rough estimate)
        # GPT-4: $0.03 per 1K tokens, GPT-3.5: $0.002 per 1K tokens
        cost_per_token = 0.03 / 1000 if "gpt-4" in self.config.model else 0.002 / 1000
        self._openai_metrics.total_cost += tokens * cost_per_token
        
        # Update last API call info
        self._last_api_call = {
            "success": success,
            "latency": latency,
            "tokens": tokens,
            "timestamp": datetime.now(UTC)
        }
    
    @property
    def openai_metrics(self) -> OpenAIMetrics:
        """Get OpenAI-specific metrics."""
        return self._openai_metrics
    
    @property
    def last_api_call(self) -> Optional[Dict[str, Any]]:
        """Get information about last API call."""
        return self._last_api_call 