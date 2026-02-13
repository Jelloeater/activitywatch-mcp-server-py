"""Tests for get_settings tool."""

import json

import httpx
import pytest
from mcp_server_activitywatch.tools.get_settings import get_settings


@pytest.mark.asyncio
async def test_returns_all_settings_when_no_key_provided(httpx_mock, mock_ctx):
    """Test returning all settings when no key is provided."""
    api_base = "http://localhost:5600/api/0"
    mock_settings = {"setting1": "value1", "setting2": "value2", "nested": {"key": "value"}}

    httpx_mock.add_response(url=f"{api_base}/settings", json=mock_settings)

    result = await get_settings(ctx=mock_ctx)

    assert isinstance(result, str)

    # Extract just the JSON part (before guidance text)
    json_text = result.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_settings


@pytest.mark.asyncio
async def test_returns_specific_setting_when_key_is_provided(httpx_mock, mock_ctx):
    """Test returning specific setting when key is provided."""
    api_base = "http://localhost:5600/api/0"
    mock_setting = "specific-value"

    httpx_mock.add_response(url=f"{api_base}/settings/setting1", json=mock_setting)

    result = await get_settings(key="setting1", ctx=mock_ctx)

    assert isinstance(result, str)
    json_text = result.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_setting


@pytest.mark.asyncio
async def test_properly_encodes_uri_components_in_key(httpx_mock, mock_ctx):
    """Test that URI components in key are properly encoded."""
    api_base = "http://localhost:5600/api/0"
    mock_setting = {"value": "test"}

    # The URL should have the key properly encoded
    httpx_mock.add_response(url=f"{api_base}/settings/complex%2Fkey%20with%20spaces", json=mock_setting)

    result = await get_settings(key="complex/key with spaces", ctx=mock_ctx)

    assert isinstance(result, str)
    json_text = result.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_setting


@pytest.mark.asyncio
async def test_handles_api_error_correctly(httpx_mock, mock_ctx):
    """Test handling API errors correctly."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_response(
        url=f"{api_base}/settings/nonexistent",
        status_code=404,
        json={"error": "Setting not found"},
    )

    result = await get_settings(key="nonexistent", ctx=mock_ctx)

    assert isinstance(result, str)
    assert "Failed to fetch settings" in result
    assert "404" in result
    assert "Setting not found" in result


@pytest.mark.asyncio
async def test_handles_network_error(httpx_mock, mock_ctx):
    """Test handling network errors."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_exception(httpx.ConnectError("Network Error"))

    result = await get_settings(ctx=mock_ctx)

    assert isinstance(result, str)
    assert "network or connection error" in result
    assert "ActivityWatch server is running" in result
