"""ActivityWatch MCP Server - Get Events Tool."""

import json
from typing import Any
from urllib.parse import urlencode

import httpx
from fastmcp import Context
from pydantic import BaseModel, Field

from ..server import mcp


class GetEventsArgs(BaseModel):
    """Arguments for get_events tool."""

    bucket_id: str = Field(..., description="ID of bucket to fetch events from")
    limit: int | None = Field(None, description="Max number of events (default: 100)")
    start: str | None = Field(None, description="Start date/time in ISO format")
    end: str | None = Field(None, description="End date/time in ISO format")


@mcp.tool(name="activitywatch-get-events")
async def get_events(
    bucket_id: str,
    limit: int | None = None,
    start: str | None = None,
    end: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Get raw events from an ActivityWatch bucket.

    Args:
        bucket_id: ID of the bucket to fetch events from
        limit: Maximum number of events to return (default: 100)
        start: Start date/time in ISO format (e.g. '2024-02-01T00:00:00Z')
        end: End date/time in ISO format (e.g. '2024-02-28T23:59:59Z')
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with event data
    """
    try:
        api_base = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"

        params: dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        url = f"{api_base}/buckets/{bucket_id}/events"
        if params:
            url += f"?{urlencode(params)}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            events = response.json()

        return json.dumps(events, indent=2)

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch events: {error} (Status code: {status_code})"

        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        if status_code == 404:
            error_message = f"""Bucket not found: {bucket_id}

Please check that you've entered the correct bucket ID. You can get a list of available buckets using the activitywatch-list-buckets tool.
"""

        return error_message

    except httpx.RequestError as error:
        api_base_display = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"
        return f"""Failed to fetch events: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running
- The API base URL is correct (currently: {api_base_display})
- No firewall or network issues are blocking the connection
"""

    except Exception as error:
        return f"Failed to fetch events: {error}"
