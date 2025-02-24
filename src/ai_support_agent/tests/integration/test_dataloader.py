"""Integration tests for the DataLoader agent."""
import pytest
from pathlib import Path
from pydantic_ai import Usage, RunContext

from ...agents.dataloader_agent import DataLoaderAgent
from ...services.pdf_processor import PDFProcessor
from ...types.agent import DataLoaderDependencies
from ...types.pdf import PDFContent, PDFProcessingError
from ...config.config import get_settings


@pytest.fixture
def pdf_processor() -> PDFProcessor:
    """Get PDF processor for testing."""
    return PDFProcessor()


@pytest.fixture
def agent_context(pdf_processor: PDFProcessor) -> RunContext:
    """Get agent context for testing."""
    deps = DataLoaderDependencies(
        usage_tracker=Usage(environment="test"),
        pdf_processor=pdf_processor
    )
    return RunContext(deps=deps)


@pytest.mark.asyncio
async def test_process_file(agent_context: RunContext) -> None:
    """Test processing a single PDF file."""
    settings = get_settings()
    test_pdf = settings.pdf_dir / "test_model.pdf"
    
    agent = DataLoaderAgent(agent_context.deps)
    content = await agent.process_file(agent_context, file_path=str(test_pdf))
    
    assert isinstance(content, PDFContent)
    assert content.model_number == "test_model"
    assert content.sections
    assert content.raw_text


@pytest.mark.asyncio
async def test_process_directory(agent_context: RunContext) -> None:
    """Test processing a directory of PDF files."""
    settings = get_settings()
    test_dir = settings.pdf_dir
    
    agent = DataLoaderAgent(agent_context.deps)
    result = await agent.process_directory(agent_context, directory=test_dir)
    
    assert result.processed_files
    assert not result.failed_files
    assert not result.error_messages


@pytest.mark.asyncio
async def test_get_product_data(agent_context: RunContext) -> None:
    """Test retrieving product data."""
    agent = DataLoaderAgent(agent_context.deps)
    content = await agent.get_product_data(agent_context, model_number="test_model")
    
    assert isinstance(content, PDFContent)
    assert content.model_number == "test_model"
    assert content.sections
    assert content.raw_text


@pytest.mark.asyncio
async def test_validate_model_number(agent_context: RunContext) -> None:
    """Test model number validation."""
    agent = DataLoaderAgent(agent_context.deps)
    
    # Test valid model
    assert await agent.validate_model_number(agent_context, model_number="test_model")
    
    # Test invalid model
    assert not await agent.validate_model_number(agent_context, model_number="invalid_model")
    assert not await agent.validate_model_number(agent_context, model_number="") 