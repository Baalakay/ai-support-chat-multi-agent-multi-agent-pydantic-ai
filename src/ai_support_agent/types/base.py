"""
Base agent implementation using PydanticAI patterns.
Provides core functionality and patterns for all agents.
"""

from typing import Optional, Dict, Any, List, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr, model_validator
from pydantic_ai import Agent, RunContext, Tool

from .agent import AgentRunContext, DepsT
from ..config.config import get_settings


class PromptTemplate(BaseModel):
    """Template for agent prompts."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "content": "Process {data} with {model}",
                    "variables": {"data": "input", "model": "gpt-4"}
                }
            ]
        }
    )
    
    content: str = Field(..., min_length=1, description="The template content")
    variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Default values for template variables"
    )
    description: Optional[str] = Field(None, description="Template description")
    examples: List[Dict[str, str]] = Field(
        default_factory=list,
        min_length=0,
        description="Example usages with variables and results"
    )
    _last_used: float = PrivateAttr(default=0.0)
    
    @computed_field(return_type=bool)
    @property
    def has_variables(self) -> bool:
        """Check if template has variables."""
        return bool(self.variables)
    
    @model_validator(mode="after")
    def validate_template(self) -> "PromptTemplate":
        """Validate template variables."""
        try:
            # Check if all variables in content are in variables dict
            format_vars = [
                name for _, name, _, _ in string.Formatter().parse(self.content)
                if name is not None
            ]
            missing = [v for v in format_vars if v not in self.variables]
            if missing:
                raise ValueError(f"Missing template variables: {', '.join(missing)}")
        except ValueError as e:
            raise ValueError(f"Template validation failed: {e}")
        return self


class PromptConfig(BaseModel):
    """Configuration for agent prompts."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True
    )

    templates: Dict[str, PromptTemplate] = Field(
        default_factory=dict,
        description="Map of template names to their content"
    )
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default variables for template formatting"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        le=32000,
        description="Maximum tokens for responses"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional prompt configuration metadata"
    )
    
    @computed_field(return_type=int)
    @property
    def template_count(self) -> int:
        """Get number of templates."""
        return len(self.templates)


class AgentResponse(BaseModel):
    """Base class for all agent responses."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response metadata"
    )


class BaseAgent(Agent[DepsT], Generic[DepsT]):
    """Base agent class providing core functionality."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        model=get_settings().default_model,
        temperature=get_settings().default_temperature
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent metadata storage"
    )

    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Base agent providing core functionality. You excel at:
        1. Processing requests accurately
        2. Maintaining consistent responses
        3. Ensuring quality output
        4. Handling errors gracefully"""

    @Agent.tool_plain
    async def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template if found, None otherwise
        """
        return self.prompt_config.templates.get(template_name)

    @Agent.tool_plain
    async def validate_confidence(self, confidence: float) -> bool:
        """Check if confidence meets threshold.
        
        Args:
            confidence: Confidence value to check
            
        Returns:
            True if confidence meets threshold
        """
        return confidence >= self.confidence_threshold

    def _format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with variables.
        
        Args:
            template_name: Name of the template in prompt_config
            **kwargs: Variables for template formatting
        
        Returns:
            Formatted prompt string
        
        Raises:
            ValueError: If template not found or formatting fails
        """
        try:
            template = self.prompt_config.templates.get(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' not found in prompt_config")
            
            # Merge default variables with provided kwargs
            variables = {**self.prompt_config.variables, **kwargs}
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt template: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting prompt template: {e}")

    async def _validate_response(self, response: Any) -> bool:
        """Validate the response from the agent.
        
        Args:
            response: Response to validate
        
        Returns:
            bool: True if validation successful
        """
        try:
            if hasattr(response, "model_validate"):
                response.model_validate(response)
                return True
            return False
        except Exception as e:
            return False

    def update_prompt_config(self, new_config: PromptConfig) -> None:
        """Update the prompt configuration.
        
        Args:
            new_config: New PromptConfig to use
        """
        self.prompt_config = new_config

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the agent.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata from the agent.
        
        Args:
            key: Metadata key
        
        Returns:
            Optional[Any]: Metadata value if found
        """
        return self.metadata.get(key)

    def clear_metadata(self) -> None:
        """Clear all metadata."""
        self.metadata.clear() 