"""
Base agent implementation using PydanticAI patterns.
Provides core functionality and patterns for all agents.
"""

from typing import Dict, List, Optional, Literal, Any, Set
from datetime import datetime, UTC
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr, model_validator
from pydantic_ai import Tool

from .differences import Difference


QueryDomain = Literal[
    "product",
    "case_study", 
    "company",
    "careers"
]


class SearchCriteria(BaseModel):
    """Search criteria for finding models."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "terms": ["voltage", "current"],
                    "filters": {"category": "electrical"},
                    "confidence_threshold": 0.8
                }
            ]
        }
    )
    
    terms: List[str] = Field(
        default_factory=list,
        description="Search terms to find relevant models"
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters to apply when searching"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for search results"
    )
    _raw_criteria: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _last_updated: datetime = PrivateAttr(default_factory=lambda: datetime.now(UTC))
    
    @computed_field(return_type=bool)
    @property
    def has_terms(self) -> bool:
        """Check if search has terms."""
        return bool(self.terms)
    
    @computed_field(return_type=bool)
    @property
    def has_filters(self) -> bool:
        """Check if search has filters."""
        return bool(self.filters)
    
    @model_validator(mode="after")
    def validate_criteria(self) -> "SearchCriteria":
        """Validate search criteria."""
        if not self.terms and not self.filters:
            raise ValueError("Must provide either search terms or filters")
        return self


class ModelTarget(BaseModel):
    """Specific model targeting information."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "model_numbers": ["520R", "980F"],
                    "search_criteria": {
                        "terms": ["voltage"],
                        "confidence_threshold": 0.8
                    }
                }
            ]
        }
    )
    
    model_numbers: List[str] = Field(
        default_factory=list,
        description="Explicit model numbers to query"
    )
    search_criteria: Optional[SearchCriteria] = Field(
        None,
        description="Search criteria for finding models"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional targeting metadata"
    )
    _raw_target: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _last_updated: datetime = PrivateAttr(default_factory=lambda: datetime.now(UTC))
    
    @computed_field(return_type=bool)
    @property
    def has_models(self) -> bool:
        """Check if target has explicit models."""
        return bool(self.model_numbers)
    
    @computed_field(return_type=bool)
    @property
    def has_search(self) -> bool:
        """Check if target has search criteria."""
        return bool(self.search_criteria)
    
    @model_validator(mode="after")
    def validate_target(self) -> "ModelTarget":
        """Validate target information."""
        if not self.model_numbers and not self.search_criteria:
            raise ValueError("Must provide either model numbers or search criteria")
        return self


class QueryIntent(BaseModel):
    """Structured understanding of user's query."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    topic: str = Field(..., description="Main topic of the query")
    sub_topic: Optional[str] = Field(None, description="Specific aspect of interest")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the query"
    )


class DisplayPreferences(BaseModel):
    """Output format preferences."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "output_format": "text",
                    "sections_to_show": ["features", "electrical", "magnetic"],
                    "show_differences_only": False,
                    "include_metadata": True
                }
            ]
        }
    )
    
    output_format: Literal["json", "text", "dataframe"] = Field(
        "text",
        description="Format to display results in"
    )
    sections_to_show: List[str] = Field(
        default_factory=lambda: ["features", "electrical", "magnetic"],
        description="Sections to include in output"
    )
    show_differences_only: bool = Field(
        False,
        description="Whether to show only differences"
    )
    include_metadata: bool = Field(
        True,
        description="Whether to include metadata in output"
    )
    
    @model_validator(mode="after")
    def validate_sections(self) -> "DisplayPreferences":
        """Validate section names."""
        valid_sections = {"features", "electrical", "magnetic", "physical", "advantages", "diagram"}
        if self.sections_to_show:
            invalid = [s for s in self.sections_to_show if s.lower() not in valid_sections]
            if invalid:
                raise ValueError(f"Invalid section names: {', '.join(invalid)}")
        return self


class TechnicalDetail(BaseModel):
    """Detailed technical analysis of a specification."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    section: str = Field(..., min_length=1, description="Section name")
    category: str = Field(..., min_length=1, description="Category name")
    specification: str = Field(..., min_length=1, description="Specification name")
    analysis: str = Field(..., min_length=1, description="Technical analysis of the specification")
    importance: Literal["high", "medium", "low"] = Field(
        ...,
        description="Importance level"
    )
