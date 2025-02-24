from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from pydantic import Field, ConfigDict, computed_field, PrivateAttr, model_validator, BaseModel
from pydantic_ai import Agent

from ..types.product import DisplayPreferences, TechnicalDetail, Difference, QueryDomain, QueryIntent


class CustomerSupportResponse(Agent):
    """Response from the Customer Support Agent."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "query_intent": {
                        "domain": "product",
                        "topic": "specifications",
                        "sub_topic": "voltage"
                    },
                    "confidence": 0.95,
                    "clarification_needed": False,
                    "display_preferences": {
                        "output_format": "json",
                        "sections_to_show": ["specifications"]
                    }
                }
            ]
        }
    )
    
    query_intent: QueryIntent = Field(..., description="Structured understanding of the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the query interpretation")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_question: Optional[str] = Field(None, description="Question to clarify intent")
    display_preferences: DisplayPreferences = Field(
        default_factory=DisplayPreferences,
        description="How to display the product information"
    )
    processing_time: float = Field(default=0.0, ge=0.0, description="Time taken to process query in seconds")
    _raw_response: str = PrivateAttr(default="")
    _processed_at: datetime = PrivateAttr(default_factory=lambda: datetime.now(UTC))
    
    @computed_field(return_type=bool)
    @property
    def needs_specialist(self) -> bool:
        """Check if specialist consultation is needed."""
        return self.confidence < 0.8 or self.clarification_needed
    
    @computed_field(return_type=bool)
    @property
    def is_high_confidence(self) -> bool:
        """Check if response has high confidence."""
        return self.confidence >= 0.9
    
    @model_validator(mode="after")
    def validate_clarification(self) -> "CustomerSupportResponse":
        """Validate clarification question is present when needed."""
        if self.clarification_needed and not self.clarification_question:
            raise ValueError("Clarification question required when clarification_needed is True")
        return self


class ProductSpecialistResponse(BaseModel):
    """Response from the Product Specialist Agent."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    technical_analysis: Dict[str, str] = Field(
        ...,
        description="Technical analysis of the product"
    )
    recommendations: List[str] = Field(
        ...,
        min_length=1,
        description="Product recommendations"
    )
    best_uses: List[str] = Field(
        ...,
        min_length=1,
        description="Best use cases"
    )
    considerations: List[str] = Field(
        ...,
        min_length=1,
        description="Important considerations"
    )
    comparative_analysis: Dict[str, str] = Field(
        default_factory=dict,
        description="Comparative analysis with other models"
    )
    
    @computed_field(return_type=bool)
    @property
    def has_differences(self) -> bool:
        """Check if comparative analysis is present."""
        return bool(self.comparative_analysis)
    
    @computed_field(return_type=bool)
    @property
    def is_high_confidence(self) -> bool:
        """Check if analysis has high confidence."""
        return self.confidence >= 0.9
    
    @computed_field(return_type=List[str])
    @property
    def key_findings(self) -> List[str]:
        """Get key findings from analysis."""
        findings = []
        if self.recommendations:
            findings.extend(self.recommendations[:2])
        if self.considerations:
            findings.extend(self.considerations[:2])
        return findings
    
    @model_validator(mode="after")
    def validate_analysis(self) -> "ProductSpecialistResponse":
        """Validate analysis completeness."""
        if not self.technical_analysis:
            raise ValueError("Technical analysis cannot be empty")
        if not self.recommendations:
            raise ValueError("Must provide at least one recommendation")
        if not self.best_uses:
            raise ValueError("Must provide at least one best use case")
        if not self.considerations:
            raise ValueError("Must provide at least one consideration")
        return self 