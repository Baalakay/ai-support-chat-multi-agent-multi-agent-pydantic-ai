"""Types for product comparison API responses."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from .differences import DifferenceAnalysis


class SpecificationValue(BaseModel):
    """Value and unit for a specification."""
    unit: Optional[str] = Field(None, description="Unit of measurement")
    value: str = Field(..., min_length=1, description="The value")
    display_value: str = Field(..., description="Formatted value with unit for display")


class ComparisonSpecification(BaseModel):
    """Specification comparison across models."""
    category: str = Field(..., description="Category within section (e.g., 'Voltage')")
    specification: str = Field(..., description="Specification name (e.g., 'Switching')")
    values: Dict[str, SpecificationValue] = Field(..., description="Model numbers to their values")
    has_differences: bool = Field(..., description="Whether values differ between models")
    analysis: Optional[DifferenceAnalysis] = Field(None, description="AI analysis of differences")


class ComparisonFeature(BaseModel):
    """Feature or advantage with presence indicators."""
    text: str = Field(..., min_length=1, description="Feature/advantage text")
    models: Dict[str, bool] = Field(..., description="Model numbers to presence indicator")


class ComparisonSection(BaseModel):
    """Section containing specifications or features."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    categories: Dict[str, List[ComparisonSpecification] | List[ComparisonFeature]] = Field(
        default_factory=dict,
        description="Specifications or features grouped by category"
    )


class ComparisonResponse(BaseModel):
    """API response for product comparison."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    model_numbers: List[str] = Field(..., min_length=2, description="Models being compared")
    comparison_id: str = Field(..., min_length=1, description="Unique identifier for this comparison")
    sections: Dict[str, ComparisonSection] = Field(default_factory=dict, description="All sections including specs, features, and advantages")
    differences_count: int = Field(default=0, ge=0, description="Number of specifications with differences") 