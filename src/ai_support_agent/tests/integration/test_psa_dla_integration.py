"""Integration tests for Product Specialist and DataLoader agent interaction."""
import pytest
from pathlib import Path
from pydantic_ai import Usage, RunContext

from ...agents.dataloader_agent import DataLoaderAgent
from ...agents.product_specialist_agent import ProductSpecialistAgent
from ...services.pdf_processor import PDFProcessor
from ...services.difference_service import DifferenceService
from ...types.agent import DataLoaderDependencies, ProductSpecialistDependencies
from ...types.pdf import PDFContent, PDFProcessingError
from ...config.config import get_settings


@pytest.fixture
def pdf_processor() -> PDFProcessor:
    """Get PDF processor for testing."""
    return PDFProcessor()


@pytest.fixture
def difference_service() -> DifferenceService:
    """Get difference service for testing."""
    return DifferenceService()


@pytest.fixture
def agent_context(pdf_processor: PDFProcessor, difference_service: DifferenceService) -> RunContext:
    """Get agent context for testing."""
    usage = Usage(environment="test")
    
    # Create data loader agent
    loader_deps = DataLoaderDependencies(
        usage_tracker=usage,
        pdf_processor=pdf_processor
    )
    loader = DataLoaderAgent(loader_deps)
    
    # Create product specialist agent
    specialist_deps = ProductSpecialistDependencies(
        usage_tracker=usage,
        difference_service=difference_service
    )
    specialist = ProductSpecialistAgent(specialist_deps)
    
    return RunContext(deps=loader_deps)


@pytest.mark.asyncio
async def test_load_and_analyze(agent_context: RunContext) -> None:
    """Test loading and analyzing a product."""
    # Get test PDF path
    settings = get_settings()
    test_pdf = settings.pdf_dir / "test_model.pdf"
    
    # Process PDF
    loader = DataLoaderAgent(agent_context.deps)
    content = await loader.process_file(agent_context, file_path=str(test_pdf))
    
    assert content is not None
    assert content.model_number == "test_model"
    assert content.sections
    
    # Create product specialist
    specialist_deps = ProductSpecialistDependencies(
        usage_tracker=agent_context.deps.usage_tracker,
        difference_service=DifferenceService()
    )
    specialist = ProductSpecialistAgent(specialist_deps)
    
    # Analyze product
    result = await specialist.analyze_product(
        RunContext(deps=specialist_deps),
        model_number="test_model"
    )
    
    assert result is not None
    assert result.confidence > 0.5
    assert result.metadata


@pytest.mark.asyncio
async def test_compare_products(agent_context: RunContext) -> None:
    """Test comparing two products."""
    # Get test PDF paths
    settings = get_settings()
    test_pdf_1 = settings.pdf_dir / "test_model_1.pdf"
    test_pdf_2 = settings.pdf_dir / "test_model_2.pdf"
    
    # Process PDFs
    loader = DataLoaderAgent(agent_context.deps)
    content_1 = await loader.process_file(agent_context, file_path=str(test_pdf_1))
    content_2 = await loader.process_file(agent_context, file_path=str(test_pdf_2))
    
    assert content_1 is not None
    assert content_2 is not None
    
    # Create product specialist
    specialist_deps = ProductSpecialistDependencies(
        usage_tracker=agent_context.deps.usage_tracker,
        difference_service=DifferenceService()
    )
    specialist = ProductSpecialistAgent(specialist_deps)
    
    # Compare products
    result = await specialist.compare_products(
        RunContext(deps=specialist_deps),
        model_a="test_model_1",
        model_b="test_model_2"
    )
    
    assert result is not None
    assert result.differences
    assert result.confidence > 0.5
    assert result.metadata 