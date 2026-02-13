"""Tests for get_events tool."""

import json

import httpx
import pytest
from mcp_server_activitywatch.tools.get_events import get_events


@pytest.fixture
def mock_events():
    """Sample event data for testing."""
    return [
        {
            "id": 1,
            "timestamp": "2024-02-19T10:00:00.000Z",
            "duration": 60.0,
            "data": {"app": "Firefox", "title": "Example Page"},
        },
        {
            "id": 2,
            "timestamp": "2024-02-19T10:01:00.000Z",
            "duration": 120.0,
            "data": {"app": "Visual Studio Code", "title": "test.py"},
        },
    ]


@pytest.mark.asyncio
async def test_fetch_events_successfully(httpx_mock, mock_events, mock_ctx):
    """Test fetching events from a bucket successfully."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "aw-watcher-window_hostname"
    httpx_mock.add_response(url=f"{api_base}/buckets/{bucket_id}/events", json=mock_events)

    result = await get_events(bucket_id=bucket_id, ctx=mock_ctx)

    assert isinstance(result, str)
    parsed_content = json.loads(result)
    assert len(parsed_content) == 2
    assert parsed_content[0]["data"]["app"] == "Firefox"
    assert parsed_content[1]["data"]["app"] == "Visual Studio Code"


@pytest.mark.asyncio
async def test_fetch_events_with_limit(httpx_mock, mock_events, mock_ctx):
    """Test fetching events with limit parameter."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "aw-watcher-window_hostname"
    httpx_mock.add_response(url=f"{api_base}/buckets/{bucket_id}/events?limit=1", json=mock_events[:1])

    result = await get_events(bucket_id=bucket_id, limit=1, ctx=mock_ctx)

    assert isinstance(result, str)
    parsed_content = json.loads(result)
    assert len(parsed_content) == 1


@pytest.mark.asyncio
async def test_fetch_events_with_start_end(httpx_mock, mock_events, mock_ctx):
    """Test fetching events with start and end parameters."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "aw-watcher-window_hostname"
    start = "2024-02-19T00:00:00Z"
    end = "2024-02-19T23:59:59Z"
    httpx_mock.add_response(
        url=f"{api_base}/buckets/{bucket_id}/events?start={start}&end={end}",
        json=mock_events,
    )

    result = await get_events(bucket_id=bucket_id, start=start, end=end, ctx=mock_ctx)

    assert isinstance(result, str)
    parsed_content = json.loads(result)
    assert len(parsed_content) == 2


@pytest.mark.asyncio
async def test_handle_bucket_not_found(httpx_mock, mock_ctx):
    """Test handling 404 error when bucket not found."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "nonexistent-bucket"
    httpx_mock.add_response(
        url=f"{api_base}/buckets/{bucket_id}/events",
        status_code=404,
        json={"error": "Bucket not found"},
    )

    result = await get_events(bucket_id=bucket_id, ctx=mock_ctx)

    assert isinstance(result, str)
    assert "Bucket not found" in result
    assert bucket_id in result
    assert "activitywatch-list-buckets" in result


@pytest.mark.asyncio
async def test_handle_api_error(httpx_mock, mock_ctx):
    """Test handling API errors with status codes."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "aw-watcher-window_hostname"
    httpx_mock.add_response(
        url=f"{api_base}/buckets/{bucket_id}/events",
        status_code=500,
        json={"error": "Internal Server Error"},
    )

    result = await get_events(bucket_id=bucket_id, ctx=mock_ctx)

    assert isinstance(result, str)
    assert "Failed to fetch events" in result
    assert "500" in result


@pytest.mark.asyncio
async def test_handle_network_errors(httpx_mock, mock_ctx):
    """Test handling network errors."""
    api_base = "http://localhost:5600/api/0"
    bucket_id = "aw-watcher-window_hostname"
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    result = await get_events(bucket_id=bucket_id, ctx=mock_ctx)

    assert isinstance(result, str)
    assert "network or connection error" in result
    assert "ActivityWatch server is running" in result
