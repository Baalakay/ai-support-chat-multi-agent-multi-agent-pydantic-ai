"""Agent for AI analysis of product differences."""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from ..types.agent import AgentDependencies
from ..types.product import QueryIntent
from ..types.differences import Difference, DifferenceAnalysis
from ..types.base import BaseAgent
from ..types.comparison import ComparisonResponse


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


class AIDifferenceAnalyzer(BaseAgent[AgentDependencies]):
    """Agent for AI analysis of product differences."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        model="gpt-4",  # Default to GPT-4 for expert analysis
        temperature=0.2,  # Low temperature for consistent technical analysis
        extra="forbid"
    )
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """You are an expert magnetic sensor application specialist providing clear, actionable recommendations.
Your task is to analyze the differences between relay models and provide strong, opinionated guidance on model selection.

Focus your analysis on these key aspects:
1. Key performance differences
2. Operating condition variations
3. Design considerations
4. Application suitability

Your response must be a JSON object with this exact structure:
{
  "findings": {
    "recommendations": [
      {
        "action": "Choose",
        "model": "HSR-520R",
        "context": "for precision applications requiring fast response times under 2ms",
        "category": "Performance Considerations"
      }
    ],
    "summary": "Brief overview of the key differences and selection criteria",
    "technical_details": "Detailed analysis of the technical specifications and their implications"
  }
}

Important:
- Every recommendation must use clear action verbs (Choose, Select, Consider, Use, Opt)
- Be specific about technical requirements and thresholds
- Provide clear, opinionated guidance
- Focus on helping engineers make decisive model selections
- Base recommendations on actual specification differences
- Group recommendations into meaningful categories

Be technical but clear. Make each recommendation actionable and specific."""

    @Agent.tool
    async def analyze_differences(
        self,
        ctx: RunContext[AgentDependencies],
        *,
        comparison: ComparisonResponse,
        query_intent: QueryIntent
    ) -> DifferenceAnalysis:
        """Analyze differences from comparison results using AI.
        
        Args:
            ctx: Runtime context with dependencies
            comparison: Results from CompareProcessor containing differences
            query_intent: What aspects to focus on
            
        Returns:
            AI analysis of the differences
            
        Raises:
            ValueError: If no differences found in comparison
        """
        try:
            if comparison.differences_count == 0:
                return DifferenceAnalysis(
                    differences=[],
                    ai_findings={
                        "findings": {
                            "recommendations": [],
                            "summary": "No differences found",
                            "technical_details": "Products have identical specifications"
                        }
                    },
                    confidence=1.0,
                    metadata={}
                )
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(comparison, query_intent)
            
            # Get AI analysis
            findings = await self.run(
                prompt=prompt,
                response_model=AIFindings,
                deps=ctx.deps
            )
            
            # Calculate confidence based on analysis quality
            confidence = self._calculate_confidence(comparison.differences_count, findings)
            
            return DifferenceAnalysis(
                differences=comparison.differences,
                ai_findings={"findings": findings.model_dump()},
                confidence=confidence,
                metadata={
                    "query_topic": query_intent.topic,
                    "query_sub_topic": query_intent.sub_topic,
                    "differences_count": comparison.differences_count,
                    "model_numbers": comparison.model_numbers
                }
            )
            
        except Exception as e:
            raise ValueError(f"Failed to analyze differences: {str(e)}")

    def _create_analysis_prompt(
        self,
        comparison: ComparisonResponse,
        query_intent: QueryIntent
    ) -> str:
        """Create prompt for difference analysis."""
        prompt_parts = [
            f"Analyze differences between models: {', '.join(comparison.model_numbers)}\n",
            "Differences:"
        ]
        
        # Process sections with differences
        for section_name, section in comparison.sections.items():
            for category_name, specs in section.categories.items():
                for spec in specs:
                    if spec.has_differences:
                        values_str = ", ".join(
                            f"{model}: {val.display_value}" 
                            for model, val in spec.values.items()
                        )
                        prompt_parts.extend([
                            f"\nSection: {section_name}",
                            f"Category: {category_name}",
                            f"Specification: {spec.specification}",
                            f"Values: {values_str}"
                        ])
        
        prompt_parts.extend([
            "\nFocus on:",
            f"- Topic: {query_intent.topic}",
            f"- Sub-topic: {query_intent.sub_topic}",
            f"- Context: {query_intent.context}",
            "\nProvide specific recommendations based on these differences.",
            "Focus on helping engineers make clear model selections.",
            "Be specific about technical requirements and thresholds."
        ])
        
        return "\n".join(prompt_parts)

    def _calculate_confidence(
        self,
        differences_count: int,
        findings: AIFindings
    ) -> float:
        """Calculate confidence in the analysis."""
        if differences_count == 0:
            return 1.0
            
        # Base confidence on recommendation quality
        rec_count = len(findings.recommendations)
        
        # More recommendations relative to differences = higher confidence
        ratio = min(rec_count / differences_count, 1.0)
        
        # Weight by recommendation specificity
        specificity = sum(
            1.0 if "specific" in rec.context else 0.5
            for rec in findings.recommendations
        ) / max(rec_count, 1)
        
        return (ratio * 0.6 + specificity * 0.4)  # Weighted average 