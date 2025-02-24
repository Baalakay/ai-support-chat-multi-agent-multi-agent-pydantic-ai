"""ProductSpecialistAgent implementation using PydanticAI v2 patterns."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from ..types.agent import AgentDependencies
from ..types.pdf import PDFContent
from ..types.differences import Difference, DifferenceAnalysis
from ..types.product import QueryIntent, DisplayPreferences
from ..tools.pdf_processor import PDFProcessor
from ..tools.compare_processor import CompareProcessor
from ..tools.ai_difference_analyzer import AIDifferenceAnalyzer
from ..config.config import get_settings
from ..types.base import BaseAgent


class ProductAnalysis(BaseModel):
    """Analysis of product specifications."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    specifications: Dict[str, Any] = Field(..., description="Filtered specifications")
    differences: Optional[List[Difference]] = Field(None, description="Identified differences")
    ai_findings: Optional[Dict[str, Any]] = Field(None, description="AI analysis of differences")
    display_format: str = Field(..., description="Format to display results in")
    sections_shown: List[str] = Field(..., description="Sections included in output")
    differences_only: bool = Field(False, description="Whether to show only differences")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProductSpecialistAgent(BaseAgent[AgentDependencies]):
    """Technical expert for product specifications and analysis."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        model=get_settings().default_model,
        temperature=get_settings().default_temperature,
        extra="forbid"
    )
    
    pdf_processor: PDFProcessor = Field(
        default_factory=PDFProcessor,
        description="Tool for processing PDFs"
    )
    compare_processor: CompareProcessor = Field(
        default_factory=CompareProcessor,
        description="Tool for comparing products"
    )
    difference_analyzer: AIDifferenceAnalyzer = Field(
        default_factory=AIDifferenceAnalyzer,
        description="Agent for analyzing differences"
    )
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Product specialist agent focused on:
        1. Analyzing product specifications
        2. Comparing multiple products
        3. Identifying key differences
        4. Providing technical insights
        5. Handling specific attribute queries
        6. Maintaining accuracy in analysis
        7. Supporting customer inquiries"""

    @Agent.tool
    async def analyze_products(
        self,
        ctx: RunContext[AgentDependencies],
        *,
        model_numbers: List[str],
        query_intent: QueryIntent,
        display_prefs: Optional[DisplayPreferences] = None
    ) -> ProductAnalysis:
        """Analyze product specifications based on query intent.
        
        Args:
            ctx: Runtime context with dependencies
            model_numbers: List of model numbers to analyze
            query_intent: Focus of analysis
            display_prefs: Output format preferences
            
        Returns:
            Analysis of product specifications
            
        Raises:
            ValueError: If products not found
        """
        try:
            # Apply display preferences
            if display_prefs is None:
                display_prefs = DisplayPreferences(
                    output_format="text",
                    sections_to_show=["all"],
                    show_differences_only=False,
                    include_metadata=True
                )
            
            # For comparison queries with multiple models
            if query_intent.topic.lower() == "comparison" and len(model_numbers) > 1:
                # Get comparison results (includes PDF processing)
                comparison = await self.compare_processor.compare_models(model_numbers)
                
                # Get AI analysis of differences if there are any
                analysis: Optional[DifferenceAnalysis] = None
                if comparison.differences_count > 0:
                    analysis = await self.difference_analyzer.analyze_differences(
                        ctx=ctx,
                        comparison=comparison,
                        query_intent=query_intent
                    )
                    
                return ProductAnalysis(
                    specifications=comparison.sections,  # Updated to use sections
                    display_format=display_prefs.output_format,
                    sections_shown=display_prefs.sections_to_show,
                    differences_only=display_prefs.show_differences_only,
                    differences=comparison.differences,
                    ai_findings=analysis.ai_findings if analysis else None,
                    metadata={
                        "models_analyzed": model_numbers,
                        "query_topic": query_intent.topic,
                        "query_sub_topic": query_intent.sub_topic,
                        "comparison_metadata": comparison.metadata,
                        "analysis_confidence": analysis.confidence if analysis else None
                    } if display_prefs.include_metadata else None
                )
            
            # For single model queries
            content = await self.pdf_processor.get_content(model_numbers[0])
            if not content:
                raise ValueError(f"No data found for model: {model_numbers[0]}")
            
            # Filter specs based on query intent
            filtered_data = await self.filter_specifications(
                ctx=ctx,
                pdf_data={model_numbers[0]: content},
                query_intent=query_intent
            )
            
            return ProductAnalysis(
                specifications=filtered_data,
                display_format=display_prefs.output_format,
                sections_shown=display_prefs.sections_to_show,
                differences_only=False,
                metadata={
                    "models_analyzed": model_numbers,
                    "query_topic": query_intent.topic,
                    "query_sub_topic": query_intent.sub_topic
                } if display_prefs.include_metadata else None
            )
            
        except Exception as e:
            raise ValueError(f"Failed to analyze products: {str(e)}")

    @Agent.tool
    async def filter_specifications(
        self,
        ctx: RunContext[AgentDependencies],
        *,
        pdf_data: Dict[str, PDFContent],
        query_intent: QueryIntent
    ) -> Dict[str, Dict[str, Any]]:
        """Filter specifications based on query intent.
        
        Args:
            ctx: Runtime context with dependencies
            pdf_data: Map of model numbers to their PDF data
            query_intent: What information is needed
            
        Returns:
            Filtered PDF data with only relevant sections and specifications
        """
        # If no specific focus, return all specs
        if not query_intent.sub_topic and not query_intent.context:
            return {model: content.sections for model, content in pdf_data.items()}
            
        prompt = f"""Extract only the relevant sections from this product data based on the query focus:

Product Data:
{pdf_data}

Query Focus:
- Topic: {query_intent.topic}
- Sub-topic: {query_intent.sub_topic}
- Context: {query_intent.context}

Return only the sections and specifications that are relevant to this specific query focus.
Maintain the section-based structure where specifications are grouped under their respective sections."""

        # Get filtered content from LLM
        response = await self.run(
            prompt=prompt,
            response_model=Dict[str, Dict[str, Any]],
            deps=ctx.deps
        )
        
        return response