"""Pytest configuration and fixtures."""

import os
from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class MockContext:
    """Mock MCP Context for testing."""

    lifespan_context: dict[str, Any]

    @classmethod
    def with_api_base(cls, api_base: str = "http://localhost:5600/api/0") -> "MockContext":
        """Create a mock context with the given api_base."""
        return cls(lifespan_context={"api_base": api_base})


@pytest.fixture(autouse=True)
def set_test_environment(request):
    """Set environment variable to indicate tests are running."""
    was_set = "PYTEST_CURRENT_TEST" in os.environ
    if not was_set:
        os.environ["PYTEST_CURRENT_TEST"] = "true"
    yield
    if not was_set and "PYTEST_CURRENT_TEST" in os.environ:
        del os.environ["PYTEST_CURRENT_TEST"]


@pytest.fixture
def mock_ctx():
    """Create a mock context with default api_base."""
    return MockContext.with_api_base()
