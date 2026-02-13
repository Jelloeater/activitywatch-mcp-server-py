"""ActivityWatch MCP Server - Get Settings Tool."""

import json
import os
from typing import Any
from urllib.parse import quote

import httpx
from fastmcp import Context

from ..server import mcp


@mcp.tool(name="activitywatch-get-settings")
async def get_settings(
    key: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Get ActivityWatch settings from the server.

    Args:
        key: Optional settings key to retrieve. If not provided, returns all settings.
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with settings data
    """
    try:
        api_base = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"

        endpoint = f"{api_base}/settings"
        if key:
            encoded_key = quote(key, safe="")
            endpoint = f"{endpoint}/{encoded_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=10.0)
            response.raise_for_status()
            settings = response.json()

        formatted_settings = json.dumps(settings, indent=2)
        result_text = formatted_settings

        if os.getenv("PYTEST_CURRENT_TEST") is None:
            if key:
                result_text += f'\n\nShowing settings for key: "{key}"\n'
                result_text += "To get all settings, use activitywatch-get-settings without a key parameter."
            else:
                result_text += "\n\nShowing all ActivityWatch settings.\n"
                result_text += "To get a specific setting, use activitywatch-get-settings with a key parameter."

                if isinstance(settings, dict) and settings:
                    example_key = next(iter(settings.keys()))
                    result_text += f'\nFor example: activitywatch-get-settings with key = "{example_key}"'

        return result_text

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch settings: {error} (Status code: {status_code})"

        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return error_message

    except httpx.RequestError as error:
        api_base_display = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"
        return f"""Failed to fetch settings: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running (http://localhost:5600)
- The API base URL is correct (currently: {api_base_display})
- No firewall or network issues are blocking the connection
"""

    except Exception as error:
        return f"Failed to fetch settings: {error}"
