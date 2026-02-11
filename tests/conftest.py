"""Pytest configuration and fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def set_test_environment(request):
    """Set environment variable to indicate tests are running."""
    # Only set if not already set by pytest
    was_set = "PYTEST_CURRENT_TEST" in os.environ
    if not was_set:
        os.environ["PYTEST_CURRENT_TEST"] = "true"
    yield
    # Only delete if we set it
    if not was_set and "PYTEST_CURRENT_TEST" in os.environ:
        del os.environ["PYTEST_CURRENT_TEST"]
