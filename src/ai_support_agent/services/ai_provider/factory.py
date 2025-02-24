"""Factory for creating LLM providers."""

from typing import Dict, Any, Optional, Type, Literal
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr
from pydantic_ai import Agent, RunContext

from .base import BaseLLMProvider, LLMConfig
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .azure import AzureProvider
from ...types.agent import AgentDependencies
from ...config.config import get_settings


ProviderType = Literal["openai", "anthropic", "azure"]


class ProviderConfig(BaseModel):
    """Configuration for provider selection."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            ]
        }
    )
    
    provider: ProviderType = Field(..., description="Provider type")
    model: str = Field(..., description="Model identifier")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    _raw_config: Dict[str, Any] = PrivateAttr(default_factory=dict)


class ProviderFactory(Agent[AgentDependencies]):
    """Factory for creating LLM providers."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid"
    )
    
    _provider_map: Dict[str, Type[BaseLLMProvider]] = PrivateAttr(default_factory=dict)
    _provider_cache: Dict[str, BaseLLMProvider] = PrivateAttr(default_factory=dict)
    _last_provider: Optional[str] = PrivateAttr(default=None)
    
    def __init__(self, **data: Any):
        """Initialize provider factory."""
        super().__init__(**data)
        self._provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "azure": AzureProvider
        }
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """LLM provider factory responsible for:
        1. Provider selection and instantiation
        2. Configuration validation
        3. Provider caching and reuse
        4. Provider metrics aggregation"""
    
    @Agent.tool
    async def get_provider(
        self,
        config: ProviderConfig,
        context: RunContext[AgentDependencies]
    ) -> BaseLLMProvider:
        """Get LLM provider instance.
        
        Args:
            config: Provider configuration
            context: Runtime context with dependencies
            
        Returns:
            Configured provider instance
            
        Raises:
            ValueError: If provider type not supported
        """
        try:
            # Create cache key
            cache_key = f"{config.provider}:{config.model}"
            
            # Check cache
            if cache_key in self._provider_cache:
                self._last_provider = cache_key
                return self._provider_cache[cache_key]
            
            # Get provider class
            provider_class = self._provider_map.get(config.provider)
            if not provider_class:
                raise ValueError(f"Unsupported provider type: {config.provider}")
            
            # Create LLM config
            llm_config = LLMConfig(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                presence_penalty=config.presence_penalty,
                frequency_penalty=config.frequency_penalty
            )
            
            # Create provider instance
            provider = provider_class(config=llm_config)
            
            # Cache provider
            self._provider_cache[cache_key] = provider
            self._last_provider = cache_key
            
            return provider
            
        except Exception as e:
            raise
    
    @Agent.tool
    async def get_default_provider(
        self,
        context: RunContext[AgentDependencies]
    ) -> BaseLLMProvider:
        """Get default provider from settings.
        
        Args:
            context: Runtime context with dependencies
            
        Returns:
            Default provider instance
        """
        settings = get_settings()
        config = ProviderConfig(
            provider="openai",  # Default to OpenAI
            model=settings.default_model,
            temperature=settings.default_temperature
        )
        return await self.get_provider(config, context)
    
    @Agent.tool_plain
    def clear_cache(self) -> None:
        """Clear provider cache."""
        self._provider_cache.clear()
        self._last_provider = None
    
    @property
    def supported_providers(self) -> list[str]:
        """Get list of supported provider types."""
        return list(self._provider_map.keys())
    
    @property
    def last_provider(self) -> Optional[str]:
        """Get last used provider."""
        return self._last_provider
    
    @property
    def cached_providers(self) -> list[str]:
        """Get list of currently cached providers."""
        return list(self._provider_cache.keys()) 