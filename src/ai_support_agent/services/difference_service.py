"""Service for analyzing differences between products."""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import RunContext

from ..types.pdf import PDFContent, PDFProcessingError
from ..types.product import QueryIntent

if TYPE_CHECKING:
    from ..types.agent import ProductSpecialistDependencies


class DifferenceResult(BaseModel):
    """Result of difference analysis."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    differences: List[str] = Field(..., description="List of key differences")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")


class DifferenceService:
    """Service for analyzing differences between products."""
    
    async def analyze_differences(
        self,
        ctx: RunContext['ProductSpecialistDependencies'],
        *,
        content_a: PDFContent,
        content_b: PDFContent,
        query: Optional[QueryIntent] = None
    ) -> DifferenceResult:
        """Analyze differences between two products.
        
        Args:
            ctx: Runtime context with dependencies
            content_a: First product content
            content_b: Second product content
            query: Optional query to focus analysis
            
        Returns:
            Analysis result with differences
            
        Raises:
            PDFProcessingError: If analysis fails
        """
        try:
            # TODO: Implement difference analysis
            differences = [
                "Product A has higher voltage rating",
                "Product B has more compact form factor"
            ]
            
            return DifferenceResult(
                differences=differences,
                confidence=0.85,
                metadata={
                    "model_a": content_a.model_number,
                    "model_b": content_b.model_number
                }
            )
            
        except Exception as e:
            raise PDFProcessingError(f"Failed to analyze differences: {e}")
    
    async def close(self) -> None:
        """Clean up resources."""
        pass

    async def get_differences(
        self,
        pdf_data_map: Dict[str, PDFContent]
    ) -> List[str]:
        """Get differences between multiple products.
        
        Args:
            pdf_data_map: Map of model numbers to their PDF data
            
        Returns:
            List of differences between products
            
        Raises:
            ValueError: If less than 2 products provided
        """
        try:
            models = list(pdf_data_map.keys())
            
            # Convert PDF data to DataFrame for comparison
            df = self._create_comparison_df(pdf_data_map)
            
            # Get differences
            differences = Differences.from_dataframe(df)
            
            return differences.differences
            
        except Exception as e:
            raise
            
    def _create_comparison_df(
        self,
        pdf_data_map: Dict[str, PDFContent]
    ) -> pd.DataFrame:
        """Create DataFrame for comparison from PDF data.
        
        Args:
            pdf_data_map: Map of model numbers to their PDF data
            
        Returns:
            DataFrame ready for comparison
        """
        # Extract specifications from each PDF
        specs_data = []
        for model, data in pdf_data_map.items():
            for category, specs in data.raw_content.items():
                if isinstance(specs, dict):
                    for spec_name, value in specs.items():
                        specs_data.append({
                            "Category": category,
                            "Specification": spec_name,
                            model: value
                        })
                        
        # Create DataFrame
        return pd.DataFrame(specs_data) 