"""Types for the differences tool."""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class Difference(BaseModel):
    """A difference between products."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    model: str = Field(..., description="Model number that has the difference")
    category: str = Field(..., description="Category the difference occurs in")
    subcategory: Optional[str] = Field(None, description="Subcategory if applicable")
    specification: str = Field(..., description="Specific value that differs")
    difference: str = Field(..., description="How it differs from other models")
    context: Optional[str] = Field(None, description="Additional context about the difference")
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    values: Dict[str, Any] = Field(default_factory=dict, description="Raw values for comparison")


class Recommendation(BaseModel):
    """Structured recommendation for model selection."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    action: Literal["Choose", "Select", "Consider", "Use", "Opt"] = Field(
        ..., description="Clear action verb for the recommendation"
    )
    model: str = Field(..., description="Model number being recommended")
    context: str = Field(..., description="Specific context or requirements")
    category: str = Field(..., description="Category of the recommendation")


class AIFindings(BaseModel):
    """Structured AI analysis findings."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    recommendations: List[Recommendation] = Field(
        ..., description="List of specific recommendations"
    )
    summary: str = Field(..., description="Overview of key differences")
    technical_details: str = Field(..., description="Detailed technical analysis")


class DifferenceAnalysis(BaseModel):
    """Analysis of differences between products."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    differences: List[Difference] = Field(..., description="List of identified differences")
    ai_findings: Dict[str, Any] = Field(..., description="AI analysis of the differences")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the analysis")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata about the analysis")

    @property
    def recommendations(self) -> List[Recommendation]:
        """Get structured recommendations from findings."""
        if "findings" in self.ai_findings:
            findings = self.ai_findings["findings"]
            if isinstance(findings, dict) and "recommendations" in findings:
                return [
                    Recommendation(**rec) 
                    for rec in findings["recommendations"]
                ]
        return []

    @property
    def summary(self) -> str:
        """Get analysis summary from findings."""
        if "findings" in self.ai_findings:
            findings = self.ai_findings["findings"]
            if isinstance(findings, dict) and "summary" in findings:
                return findings["summary"]
        return "No summary available"

    @property
    def technical_details(self) -> str:
        """Get technical details from findings."""
        if "findings" in self.ai_findings:
            findings = self.ai_findings["findings"]
            if isinstance(findings, dict) and "technical_details" in findings:
                return findings["technical_details"]
        return "No technical details available"


class Differences(BaseModel):
    """Collection of differences between products."""
    differences: List[Difference] = Field(default_factory=list, description="List of differences between products")

    def add_difference(
        self,
        category: str,
        subcategory: Optional[str],
        specification: str,
        values: Dict[str, str],
        unit: Optional[str] = None,
        impact: Optional[str] = None,
        recommendation: Optional[str] = None,
        analysis: Optional[DifferenceAnalysis] = None
    ) -> None:
        """Add a new difference if values are actually different."""
        diff = Difference(
            category=category,
            subcategory=subcategory,
            specification=specification,
            values=values,
            unit=unit,
            impact=impact,
            recommendation=recommendation,
            analysis=analysis
        )
        # Only add if values are actually different
        unique_values = {v for v in values.values() if v}
        if len(unique_values) > 1:
            self.differences.append(diff) 