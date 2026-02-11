"""ActivityWatch MCP Server - Get Events Tool."""

import json
from typing import Any
from urllib.parse import urlencode

import httpx
from mcp.types import TextContent
from pydantic import BaseModel, Field


class GetEventsArgs(BaseModel):
    """Arguments for get_events tool."""

    bucket_id: str = Field(..., description="ID of bucket to fetch events from")
    limit: int | None = Field(None, description="Max number of events (default: 100)")
    start: str | None = Field(None, description="Start date/time in ISO format")
    end: str | None = Field(None, description="End date/time in ISO format")


def get_events_schema() -> dict[str, Any]:
    """Return the JSON schema for get_events tool."""
    return {
        "type": "object",
        "properties": {
            "bucket_id": {
                "type": "string",
                "description": "ID of the bucket to fetch events from",
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of events to return (default: 100)",
            },
            "start": {
                "type": "string",
                "description": "Start date/time in ISO format (e.g. '2024-02-01T00:00:00Z')",
            },
            "end": {
                "type": "string",
                "description": "End date/time in ISO format (e.g. '2024-02-28T23:59:59Z')",
            },
        },
        "required": ["bucket_id"],
    }


async def get_events_handler(
    api_base: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Get raw events from an ActivityWatch bucket.

    Args:
        api_base: ActivityWatch API base URL
        arguments: Tool arguments (bucket_id and optional filters)

    Returns:
        List of TextContent with event data
    """
    try:
        # Parse and validate arguments
        args = GetEventsArgs(**arguments)

        # Build query parameters
        params: dict[str, str] = {}
        if args.limit is not None:
            params["limit"] = str(args.limit)
        if args.start:
            params["start"] = args.start
        if args.end:
            params["end"] = args.end

        # Build URL
        url = f"{api_base}/buckets/{args.bucket_id}/events"
        if params:
            url += f"?{urlencode(params)}"

        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            events = response.json()

        # Format response
        result_text = json.dumps(events, indent=2)

        return [TextContent(type="text", text=result_text)]

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch events: {error} (Status code: {status_code})"

        # Try to include response data
        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        # Special handling for 404 errors
        if status_code == 404:
            bucket_id = arguments.get("bucket_id", "unknown")
            error_message = f"""Bucket not found: {bucket_id}

Please check that you've entered the correct bucket ID. You can get a list of available buckets using the activitywatch-list-buckets tool.
"""

        return [TextContent(type="text", text=error_message)]

    except httpx.RequestError as error:
        error_message = f"""Failed to fetch events: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running
- The API base URL is correct (currently: {api_base})
- No firewall or network issues are blocking the connection
"""
        return [TextContent(type="text", text=error_message)]

    except Exception as error:
        return [TextContent(type="text", text=f"Failed to fetch events: {error}")]
