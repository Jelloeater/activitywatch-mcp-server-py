"""ActivityWatch MCP Server - Get Settings Tool."""

import json
import os
from typing import Any
from urllib.parse import quote

import httpx
from mcp.types import TextContent
from pydantic import BaseModel, Field


class GetSettingsArgs(BaseModel):
    """Arguments for get_settings tool."""

    key: str | None = Field(None, description="Get specific settings key")


def get_settings_schema() -> dict[str, Any]:
    """Return the JSON schema for get_settings tool."""
    return {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Optional: Get a specific settings key instead of all settings",
            },
        },
    }


async def get_settings_handler(
    api_base: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Get ActivityWatch settings.

    Args:
        api_base: ActivityWatch API base URL
        arguments: Tool arguments (optional key)

    Returns:
        List of TextContent with settings data
    """
    try:
        # Parse and validate arguments
        args = GetSettingsArgs(**arguments)

        # Build endpoint URL
        endpoint = f"{api_base}/settings"
        if args.key:
            # Properly encode the key for use in URL path
            encoded_key = quote(args.key, safe="")
            endpoint = f"{endpoint}/{encoded_key}"

        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=10.0)
            response.raise_for_status()
            settings = response.json()

        # Format settings data
        formatted_settings = json.dumps(settings, indent=2)
        result_text = formatted_settings

        # Add helpful guidance (not in test mode)
        if os.getenv("PYTEST_CURRENT_TEST") is None:
            if args.key:
                result_text += f'\n\nShowing settings for key: "{args.key}"\n'
                result_text += (
                    "To get all settings, use activitywatch-get-settings without a key parameter."
                )
            else:
                result_text += "\n\nShowing all ActivityWatch settings.\n"
                result_text += "To get a specific setting, use activitywatch-get-settings with a key parameter."

                # Add example of a specific key if there are any settings
                if isinstance(settings, dict) and settings:
                    example_key = next(iter(settings.keys()))
                    result_text += (
                        f'\nFor example: activitywatch-get-settings with key = "{example_key}"'
                    )

        return [TextContent(type="text", text=result_text)]

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch settings: {error} (Status code: {status_code})"

        # Try to include response data
        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return [TextContent(type="text", text=error_message)]

    except httpx.RequestError as error:
        error_message = f"""Failed to fetch settings: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running (http://localhost:5600)
- The API base URL is correct (currently: {api_base})
- No firewall or network issues are blocking the connection
"""
        return [TextContent(type="text", text=error_message)]

    except Exception as error:
        return [TextContent(type="text", text=f"Failed to fetch settings: {error}")]
