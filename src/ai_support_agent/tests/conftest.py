"""Test configuration and fixtures."""
import pytest
import warnings
from datetime import datetime, UTC
from typing import Generator

from pydantic_ai import RunContext
from pydantic_ai.usage import Usage

from ..config.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configure test environment."""
    # Disable all warnings
    warnings.simplefilter("ignore")
    
    yield


@pytest.fixture
def ctx() -> RunContext:
    """Create run context for testing."""
    return RunContext(
        deps=None,  # No dependencies needed for tests
        model="test-model",
        usage=Usage(
            requests=0,
            request_tokens=None,
            response_tokens=None,
            total_tokens=None,
            details=None
        ),
        prompt="Test prompt"
    ) 