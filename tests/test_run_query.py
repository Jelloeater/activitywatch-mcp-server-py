"""Tests for run_query tool."""

import json

import httpx
import pytest
from mcp_server_activitywatch.tools.run_query import run_query


@pytest.mark.asyncio
async def test_execute_simple_query_successfully(httpx_mock, mock_ctx):
    """Test executing a simple query successfully."""
    api_base = "http://localhost:5600/api/0"
    mock_response = {
        "2024-02-01_2024-02-07": [
            {"duration": 3600, "app": "Firefox"},
            {"duration": 1800, "app": "Visual Studio Code"},
        ]
    }

    httpx_mock.add_response(url=f"{api_base}/query/", json=mock_response)

    result = await run_query(
        timeperiods=["2024-02-01/2024-02-07"],
        query=['afk_events = query_bucket("aw-watcher-afk_hostname"); RETURN = afk_events;'],
        ctx=mock_ctx,
    )

    assert isinstance(result, str)

    parsed_content = json.loads(result)
    assert "2024-02-01_2024-02-07" in parsed_content
    assert len(parsed_content["2024-02-01_2024-02-07"]) == 2


@pytest.mark.asyncio
async def test_include_name_parameter_when_provided(httpx_mock, mock_ctx):
    """Test including name parameter in URL when provided."""
    api_base = "http://localhost:5600/api/0"
    mock_response = {"result": "success"}

    httpx_mock.add_response(url=f"{api_base}/query/?name=my-test-query", json=mock_response)

    result = await run_query(
        timeperiods=["2024-02-01/2024-02-07"],
        query=['RETURN = "test";'],
        name="my-test-query",
        ctx=mock_ctx,
    )

    assert isinstance(result, str)
    parsed_content = json.loads(result)
    assert parsed_content["result"] == "success"


@pytest.mark.asyncio
async def test_handle_query_errors_with_response_data(httpx_mock, mock_ctx):
    """Test handling query errors with response data."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_response(
        url=f"{api_base}/query/",
        status_code=400,
        json={"error": "Query syntax error"},
    )

    result = await run_query(
        timeperiods=["2024-02-01/2024-02-07"],
        query=["invalid query syntax"],
        ctx=mock_ctx,
    )

    assert isinstance(result, str)
    assert "Query failed" in result
    assert "400" in result
    assert "Query syntax error" in result


@pytest.mark.asyncio
async def test_handle_network_errors(httpx_mock, mock_ctx):
    """Test handling network errors."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_exception(httpx.ConnectError("Network Error"))

    result = await run_query(
        timeperiods=["2024-02-01/2024-02-07"],
        query=['RETURN = "test";'],
        ctx=mock_ctx,
    )

    assert isinstance(result, str)
    assert "Query failed" in result


@pytest.mark.asyncio
async def test_format_timeperiods_correctly(httpx_mock, mock_ctx):
    """Test that timeperiods are formatted correctly."""
    api_base = "http://localhost:5600/api/0"
    mock_response = {"result": "success"}

    httpx_mock.add_response(url=f"{api_base}/query/", json=mock_response)

    # Test with two separate dates (should be combined)
    result = await run_query(
        timeperiods=["2024-02-01", "2024-02-07"],
        query=['RETURN = "test";'],
        ctx=mock_ctx,
    )

    assert isinstance(result, str)
    # Verify the request was made (httpx_mock will verify URL was called)
