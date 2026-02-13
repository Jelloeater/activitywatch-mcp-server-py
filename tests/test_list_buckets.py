"""Tests for list_buckets tool."""

import json

import httpx
import pytest
from mcp_server_activitywatch.tools.list_buckets import list_buckets


@pytest.fixture
def mock_buckets():
    """Sample bucket data for testing."""
    return {
        "aw-watcher-window_hostname": {
            "type": "window",
            "client": "aw-watcher-window",
            "hostname": "hostname",
            "created": "2024-02-19T10:00:00.000Z",
            "data": {"key": "value"},
        }
    }


@pytest.mark.asyncio
async def test_fetch_and_format_buckets_correctly(httpx_mock, mock_buckets, mock_ctx):
    """Test fetching and formatting buckets correctly."""
    api_base = "http://localhost:5600/api/0"
    httpx_mock.add_response(url=f"{api_base}/buckets", json=mock_buckets)

    result = await list_buckets(ctx=mock_ctx)

    assert isinstance(result, str)

    parsed_content = json.loads(result.split("\n\n")[0])  # Split to ignore guidance
    assert len(parsed_content) == 1
    assert parsed_content[0]["type"] == "window"
    assert "data" not in parsed_content[0]  # data not included by default
    assert parsed_content[0]["id"] == "aw-watcher-window_hostname"


@pytest.mark.asyncio
async def test_filter_buckets_by_type_case_insensitively(httpx_mock, mock_ctx):
    """Test filtering buckets by type (case-insensitive)."""
    api_base = "http://localhost:5600/api/0"
    mock_buckets = {
        "aw-watcher-window_hostname": {
            "type": "window",
            "client": "aw-watcher-window",
            "hostname": "hostname",
            "created": "2024-02-19T10:00:00.000Z",
        },
        "aw-watcher-afk_hostname": {
            "type": "afk",
            "client": "aw-watcher-afk",
            "hostname": "hostname",
            "created": "2024-02-19T10:00:00.000Z",
        },
    }
    httpx_mock.add_response(url=f"{api_base}/buckets", json=mock_buckets)

    # Test with uppercase filter
    result = await list_buckets(type="WINDOW", ctx=mock_ctx)
    parsed_content = json.loads(result.split("\n\n")[0])

    assert len(parsed_content) == 1
    assert parsed_content[0]["type"] == "window"


@pytest.mark.asyncio
async def test_include_data_when_requested(httpx_mock, mock_buckets, mock_ctx):
    """Test including data when include_data is True."""
    api_base = "http://localhost:5600/api/0"
    httpx_mock.add_response(url=f"{api_base}/buckets", json=mock_buckets)

    result = await list_buckets(include_data=True, ctx=mock_ctx)
    parsed_content = json.loads(result.split("\n\n")[0])

    assert "data" in parsed_content[0]
    assert parsed_content[0]["data"]["key"] == "value"


@pytest.mark.asyncio
async def test_handle_api_errors_with_status_codes(httpx_mock, mock_ctx):
    """Test handling API errors with status codes."""
    api_base = "http://localhost:5600/api/0"
    httpx_mock.add_response(url=f"{api_base}/buckets", status_code=404, json={"error": "Not Found"})

    result = await list_buckets(ctx=mock_ctx)

    assert isinstance(result, str)
    assert "Failed to fetch buckets" in result
    assert "404" in result


@pytest.mark.asyncio
async def test_handle_network_errors(httpx_mock, mock_ctx):
    """Test handling network errors."""
    api_base = "http://localhost:5600/api/0"
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    result = await list_buckets(ctx=mock_ctx)

    assert isinstance(result, str)
    assert "network or connection error" in result
    assert "ActivityWatch server is running" in result
