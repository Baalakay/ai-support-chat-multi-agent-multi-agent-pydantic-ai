"""Product-related API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from ..dependencies import get_agent_context, get_customer_support_agent
from ..types.product import QueryIntent, DisplayPreferences
from ..domain.agent_responses import CustomerSupportResponse, ProductSpecialistResponse
from ..types.storage import PDFData


router = APIRouter(
    prefix="/api/products",
    tags=["products"],
    responses={
        404: {"description": "Product not found"},
        500: {"description": "Internal server error"}
    }
)


class ProductQuery(BaseModel):
    """Product query parameters."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    query: str = Field(..., description="The customer's query text")
    model_numbers: List[str] = Field(..., description="List of product model numbers to analyze")
    display_preferences: Optional[DisplayPreferences] = Field(
        default=None,
        description="Display preferences for the results"
    )


class ProductResponse(BaseModel):
    """Combined response from agents."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    customer_support: CustomerSupportResponse
    product_specialist: Optional[ProductSpecialistResponse] = None
    metadata: dict = Field(default_factory=dict)


@router.post(
    "/analyze",
    response_model=ProductResponse,
    summary="Analyze products",
    description="Analyze products using customer support agent"
)
async def analyze_products(
    query: ProductQuery,
    context = Depends(get_agent_context),
    customer_support = Depends(get_customer_support_agent)
) -> ProductResponse:
    """
    Analyze products using the customer support agent.
    
    Args:
        query: Product query parameters
        context: Agent runtime context
        customer_support: Customer support agent instance
    
    Returns:
        Combined analysis from the agents
    
    Raises:
        HTTPException: If products not found or analysis fails
    """
    try:
        # Create query intent
        query_intent = QueryIntent(
            domain="product",
            topic=query.model_numbers,
            sub_topic="specifications",
            display_preferences=query.display_preferences or DisplayPreferences()
        )
        
        # Get customer support analysis
        cs_response = await customer_support.analyze_query(
            query=query.query,
            context=context
        )
        
        return ProductResponse(
            customer_support=cs_response,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "query": query.dict()
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/{model_number}/specs",
    response_model=TechnicalSpecs,
    summary="Get product specifications",
    description="Get technical specifications for a specific product",
    response_description="Product technical specifications"
)
async def get_product_specs(
    model_number: str = Path(..., description="Product model number"),
    sections: Optional[List[str]] = Query(None, description="Specific sections to include")
) -> TechnicalSpecs:
    """
    Get technical specifications for a product.
    
    Args:
        model_number: Product model number
        sections: Optional list of specific sections to include
    
    Returns:
        Product technical specifications
    
    Raises:
        HTTPException: If product not found
    """
    try:
        specs = await get_product_specs_from_db(model_number)
        if sections:
            specs = filter_specs_sections(specs, sections)
        return specs
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 