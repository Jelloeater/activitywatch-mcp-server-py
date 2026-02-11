"""Tests for get_settings tool."""

import json

import httpx
import pytest
from mcp_server_activitywatch.tools.get_settings import get_settings_handler


@pytest.mark.asyncio
async def test_returns_all_settings_when_no_key_provided(httpx_mock):
    """Test returning all settings when no key is provided."""
    api_base = "http://localhost:5600/api/0"
    mock_settings = {"setting1": "value1", "setting2": "value2", "nested": {"key": "value"}}

    httpx_mock.add_response(url=f"{api_base}/settings", json=mock_settings)

    result = await get_settings_handler(api_base, {})

    assert len(result) == 1
    assert result[0].type == "text"

    # Extract just the JSON part (before guidance text)
    json_text = result[0].text.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_settings


@pytest.mark.asyncio
async def test_returns_specific_setting_when_key_is_provided(httpx_mock):
    """Test returning specific setting when key is provided."""
    api_base = "http://localhost:5600/api/0"
    mock_setting = "specific-value"

    httpx_mock.add_response(url=f"{api_base}/settings/setting1", json=mock_setting)

    result = await get_settings_handler(api_base, {"key": "setting1"})

    assert len(result) == 1
    json_text = result[0].text.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_setting


@pytest.mark.asyncio
async def test_properly_encodes_uri_components_in_key(httpx_mock):
    """Test that URI components in key are properly encoded."""
    api_base = "http://localhost:5600/api/0"
    mock_setting = {"value": "test"}

    # The URL should have the key properly encoded
    httpx_mock.add_response(
        url=f"{api_base}/settings/complex%2Fkey%20with%20spaces", json=mock_setting
    )

    result = await get_settings_handler(api_base, {"key": "complex/key with spaces"})

    assert len(result) == 1
    json_text = result[0].text.split("\n\n")[0]
    parsed_content = json.loads(json_text)
    assert parsed_content == mock_setting


@pytest.mark.asyncio
async def test_handles_api_error_correctly(httpx_mock):
    """Test handling API errors correctly."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_response(
        url=f"{api_base}/settings/nonexistent",
        status_code=404,
        json={"error": "Setting not found"},
    )

    result = await get_settings_handler(api_base, {"key": "nonexistent"})

    assert len(result) == 1
    assert "Failed to fetch settings" in result[0].text
    assert "404" in result[0].text
    assert "Setting not found" in result[0].text


@pytest.mark.asyncio
async def test_handles_network_error(httpx_mock):
    """Test handling network errors."""
    api_base = "http://localhost:5600/api/0"

    httpx_mock.add_exception(httpx.ConnectError("Network Error"))

    result = await get_settings_handler(api_base, {})

    assert len(result) == 1
    assert "network or connection error" in result[0].text
    assert "ActivityWatch server is running" in result[0].text
