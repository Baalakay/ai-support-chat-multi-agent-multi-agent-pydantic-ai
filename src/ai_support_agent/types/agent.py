"""
Type definitions for agent system.
Provides core types, protocols and dependencies for the agent system.
"""

from typing import Protocol, TypeVar, Optional, Literal, TYPE_CHECKING, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr, model_validator
from pydantic_ai import RunContext, Tool, Agent
from pydantic_ai.usage import Usage

from ..tools.pdf_processor import PDFProcessor
from ..config.config import get_settings

# Forward references
if TYPE_CHECKING:
    from ..agents.product_specialist_agent import ProductSpecialistAgent
    from ..services.difference_service import DifferenceService

# Type variables
ResponseT = TypeVar('ResponseT', bound=BaseModel)
DepsT = TypeVar('DepsT', bound='AgentDependencies')

class DisplayPreferences(BaseModel):
    """User display preferences for output formatting."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,  # Add strict mode
        json_schema_extra={
            "examples": [
                {
                    "output_format": "json",
                    "sections_to_show": ["features", "specs"],
                    "show_differences_only": True
                }
            ]
        }
    )
    
    output_format: Literal["json", "text", "dataframe"] = Field(
        default="json",
        description="Desired output format"
    )
    sections_to_show: List[str] = Field(
        default_factory=list,
        min_length=0,
        description="Sections to include in output"
    )
    show_differences_only: bool = Field(
        default=False,
        description="Whether to show only differences in comparisons"
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include metadata in output"
    )
    _last_used: float = PrivateAttr(default=0.0)
    
    @computed_field(return_type=bool)
    @property
    def has_sections(self) -> bool:
        """Check if specific sections are requested."""
        return bool(self.sections_to_show)
    
    @model_validator(mode="after")
    def validate_sections(self) -> "DisplayPreferences":
        """Validate section names."""
        if self.sections_to_show:
            valid_sections = {"features", "specs", "advantages", "differences"}
            invalid = [s for s in self.sections_to_show if s not in valid_sections]
            if invalid:
                raise ValueError(f"Invalid section names: {', '.join(invalid)}")
        return self

class AgentDependencies(BaseModel):
    """Core dependencies shared across all agents."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        validate_assignment=True,
        strict=True
    )
    
    usage_tracker: Usage = Field(..., description="Usage tracking for the agent")
    model_name: str = Field(
        default=get_settings().default_model,
        min_length=1,
        description="OpenAI model name"
    )
    temperature: float = Field(
        default=get_settings().default_temperature,
        ge=0.0,
        le=1.0,
        description="Model temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for model response"
    )
    environment: str = Field(
        default="development",
        description="Environment (development/test/production)"
    )
    display_preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Display preferences for output formatting"
    )
    _initialized_at: float = PrivateAttr(default=0.0)
    
    @computed_field(return_type=bool)
    @property
    def is_configured(self) -> bool:
        """Check if all required services are configured."""
        return bool(self.usage_tracker)
    
    @model_validator(mode="after")
    def validate_dependencies(self) -> "AgentDependencies":
        """Validate dependencies are properly configured."""
        if not self.usage_tracker:
            raise ValueError("Usage tracker is required")
        return self

class DataLoaderDependencies(AgentDependencies):
    """Dependencies specific to the DataLoader agent."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        validate_assignment=True,
        strict=True  # Add strict mode
    )
    
    pdf_processor: PDFProcessor = Field(..., description="PDF processing tool")
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Model temperature"
    )  # Lower temperature for consistent processing
    
    @model_validator(mode="after")
    def validate_pdf_processor(self) -> "DataLoaderDependencies":
        """Validate PDF processor is properly configured."""
        return self

# Rebuild model to ensure all types are properly resolved
DataLoaderDependencies.model_rebuild()

class ProductSpecialistDependencies(AgentDependencies):
    """Dependencies specific to the Product Specialist agent."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        validate_assignment=True,
        strict=True  # Add strict mode
    )
    
    difference_service: 'DifferenceService' = Field(..., description="Service for analyzing differences")
    
    @model_validator(mode="after")
    def validate_difference_service(self) -> "ProductSpecialistDependencies":
        """Validate difference service is configured."""
        if not self.difference_service:
            raise ValueError("Difference service is required")
        return self

class CustomerSupportDependencies(AgentDependencies):
    """Dependencies specific to the Customer Support agent."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        validate_assignment=True,
        strict=True  # Add strict mode
    )
    
    product_specialist: 'ProductSpecialistAgent' = Field(..., description="Product specialist agent for technical analysis")
    
    @model_validator(mode="after")
    def validate_product_specialist(self) -> "CustomerSupportDependencies":
        """Validate product specialist is configured."""
        if not self.product_specialist:
            raise ValueError("Product specialist is required")
        return self

class AgentResponse(BaseModel):
    """Base response model for all agents."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,  # Add strict mode
        json_schema_extra={
            "examples": [
                {
                    "confidence": 0.95,
                    "metadata": {"source": "gpt-4", "tokens": 150}
                }
            ]
        }
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the response"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )
    _raw_response: str = PrivateAttr(default="")
    
    @computed_field(return_type=bool)
    @property
    def is_high_confidence(self) -> bool:
        """Check if response has high confidence."""
        return self.confidence >= 0.9
    
    @model_validator(mode="after")
    def validate_metadata(self) -> "AgentResponse":
        """Validate required metadata fields."""
        required_fields = {"source", "tokens"}
        if self.metadata:
            missing = required_fields - set(self.metadata.keys())
            if missing:
                raise ValueError(f"Missing required metadata fields: {missing}")
        return self

class AgentRunContext(Protocol[DepsT]):
    """Protocol defining required context methods."""
    dependencies: DepsT
    
    @property
    def usage(self) -> Usage:
        """Get usage tracker."""
        ...
    
    @property
    def model(self) -> str:
        """Get model name."""
        ...
    
    def with_model(self, model_name: str) -> 'AgentRunContext[DepsT]':
        """Create new context with different model."""
        ...
    
    def with_temperature(self, temperature: float) -> 'AgentRunContext[DepsT]':
        """Create new context with different temperature."""
        ...
    
    def with_display_preferences(self, preferences: DisplayPreferences) -> 'AgentRunContext[DepsT]':
        """Create new context with different display preferences."""
        ...

class AgentProtocol(Protocol[ResponseT]):
    """Protocol defining required agent methods."""
    def get_system_message(self) -> str: ...
    
    async def analyze_query(
        self, 
        query: str,
        context: AgentRunContext[AgentDependencies]
    ) -> ResponseT: ...
