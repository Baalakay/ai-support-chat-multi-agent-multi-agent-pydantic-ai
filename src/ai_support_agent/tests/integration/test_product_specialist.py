"""Integration tests for the Product Specialist agent."""
import pytest
from pathlib import Path
from pydantic_ai import Usage, RunContext

from ...agents.product_specialist_agent import ProductSpecialistAgent
from ...services.difference_service import DifferenceService
from ...types.agent import ProductSpecialistDependencies
from ...types.pdf import PDFContent, PDFProcessingError
from ...types.product import QueryIntent, QueryDomain
from ...config.config import get_settings


@pytest.fixture
def difference_service() -> DifferenceService:
    """Get difference service for testing."""
    return DifferenceService()


@pytest.fixture
def agent_context(difference_service: DifferenceService) -> RunContext:
    """Get agent context for testing."""
    deps = ProductSpecialistDependencies(
        usage_tracker=Usage(environment="test"),
        difference_service=difference_service
    )
    return RunContext(deps=deps)


@pytest.mark.asyncio
async def test_analyze_product(agent_context: RunContext) -> None:
    """Test analyzing a single product."""
    agent = ProductSpecialistAgent(agent_context.deps)
    result = await agent.analyze_product(
        agent_context,
        model_number="test_model",
        query=QueryIntent(
            domain=QueryDomain.PRODUCT,
            query="What are the key features?",
            sub_topic="features"
        )
    )
    
    assert result is not None
    assert result.confidence > 0.5
    assert result.metadata


@pytest.mark.asyncio
async def test_compare_products(agent_context: RunContext) -> None:
    """Test comparing two products."""
    agent = ProductSpecialistAgent(agent_context.deps)
    result = await agent.compare_products(
        agent_context,
        model_a="test_model_1",
        model_b="test_model_2",
        query=QueryIntent(
            domain=QueryDomain.COMPARISON,
            query="What are the main differences?",
            sub_topic="differences"
        )
    )
    
    assert result is not None
    assert result.differences
    assert result.confidence > 0.5
    assert result.metadata


@pytest.mark.asyncio
async def test_analyze_features(agent_context: RunContext) -> None:
    """Test analyzing product features."""
    agent = ProductSpecialistAgent(agent_context.deps)
    result = await agent.analyze_features(
        agent_context,
        model_number="test_model",
        query=QueryIntent(
            domain=QueryDomain.FEATURES,
            query="What are the advantages?",
            sub_topic="advantages"
        )
    )
    
    assert result is not None
    assert result.features
    assert result.confidence > 0.5
    assert result.metadata 