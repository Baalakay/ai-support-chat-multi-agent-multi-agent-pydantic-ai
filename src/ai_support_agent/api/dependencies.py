"""
FastAPI dependencies for the API endpoints.
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Query
from pydantic_ai.usage import Usage  # For type hints and instance creation
from pydantic_ai import RunContext

from ..config.config import get_settings
from ..types.agent import AgentDependencies, DisplayPreferences
from ..services.storage_service import SupabaseStorageService
from ..services.difference_service import DifferenceService
from ..agents.customer_support_agent import CustomerSupportAgent
from ..agents.product_specialist_agent import ProductSpecialistAgent
from ..agents.dataloader_agent import DataLoaderAgent
from ..services.pdf_processor import PDFProcessor
from ..types.agent import (
    DataLoaderDependencies,
    ProductSpecialistDependencies,
    CustomerSupportDependencies
)


async def get_display_preferences(
    output_format: str = Query("json", description="Desired output format"),
    sections: Optional[list[str]] = Query(None, description="Sections to include"),
    differences_only: bool = Query(False, description="Show only differences"),
    include_metadata: bool = Query(True, description="Include metadata")
) -> DisplayPreferences:
    """Get display preferences from query parameters."""
    return DisplayPreferences(
        output_format=output_format,
        sections_to_show=sections or [],
        show_differences_only=differences_only,
        include_metadata=include_metadata
    )


async def get_agent_context(
    display_prefs: DisplayPreferences = Depends(get_display_preferences)
) -> RunContext[AgentDependencies]:
    """Get configured RunContext with dependencies for agents."""
    try:
        settings = get_settings()
        
        # Initialize core services
        storage_service = SupabaseStorageService(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key
        )
        difference_service = DifferenceService()
        usage_tracker = Usage()  # Use Usage class directly

        # Create dependencies
        dependencies = AgentDependencies(
            usage_tracker=usage_tracker,
            storage_service=storage_service,
            difference_service=difference_service,
            model_name=settings.default_model,
            temperature=settings.default_temperature,
            display_preferences=display_prefs
        )

        return RunContext(dependencies=dependencies)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize agent context"
        )


async def get_usage() -> AsyncGenerator[Usage, None]:
    """Get usage tracking instance."""
    usage = Usage(environment="development")
    try:
        yield usage
    finally:
        await usage.close()


async def get_pdf_processor() -> AsyncGenerator[PDFProcessor, None]:
    """Get PDF processor instance."""
    processor = PDFProcessor()
    try:
        yield processor
    finally:
        await processor.close()


async def get_difference_service() -> AsyncGenerator[DifferenceService, None]:
    """Get difference analysis service."""
    service = DifferenceService()
    try:
        yield service
    finally:
        await service.close()


async def get_dataloader_agent(
    usage: Usage = Depends(get_usage),
    pdf_processor: PDFProcessor = Depends(get_pdf_processor)
) -> AsyncGenerator[DataLoaderAgent, None]:
    """Get data loader agent instance."""
    deps = DataLoaderDependencies(
        usage_tracker=usage,
        pdf_processor=pdf_processor
    )
    agent = DataLoaderAgent(deps)
    try:
        yield agent
    finally:
        await agent.close()


async def get_product_specialist_agent(
    usage: Usage = Depends(get_usage),
    difference_service: DifferenceService = Depends(get_difference_service)
) -> AsyncGenerator[ProductSpecialistAgent, None]:
    """Get product specialist agent instance."""
    deps = ProductSpecialistDependencies(
        usage_tracker=usage,
        difference_service=difference_service
    )
    agent = ProductSpecialistAgent(deps)
    try:
        yield agent
    finally:
        await agent.close()


async def get_customer_support_agent(
    usage: Usage = Depends(get_usage),
    product_specialist: ProductSpecialistAgent = Depends(get_product_specialist_agent)
) -> AsyncGenerator[CustomerSupportAgent, None]:
    """Get customer support agent instance."""
    deps = CustomerSupportDependencies(
        usage_tracker=usage,
        product_specialist=product_specialist
    )
    agent = CustomerSupportAgent(deps)
    try:
        yield agent
    finally:
        await agent.close() 