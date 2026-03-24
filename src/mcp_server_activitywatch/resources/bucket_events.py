"""ActivityWatch MCP Server - Bucket Events Resource.

This module provides MCP resource templates for accessing bucket events.
Resource templates are parameterized resources that accept values in the URI.
"""

import httpx
from fastmcp import Context

from ..server import mcp


@mcp.resource(
    uri="activitywatch://events/{bucket_id}",
    name="Bucket Events",
    description="Retrieves events from a specific ActivityWatch bucket. Use this to get raw event data from buckets like afk, window, or editor.",
)
async def bucket_events_resource(
    bucket_id: str,
    start: str | None = None,
    end: str | None = None,
    limit: int | None = None,
    ctx: Context | None = None,
) -> str:
    """Fetch events from a specific bucket as a resource.

    This resource template allows reading bucket events directly without
    invoking the get-events tool.

    Args:
        bucket_id: The bucket identifier to fetch events from
        start: Start datetime in ISO format (optional)
        end: End datetime in ISO format (optional)
        limit: Maximum number of events to return (optional)
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with bucket events
    """
    try:
        api_base = ctx.lifespan_context.get("api_base", "http://localhost:5600/api/0")

        # Build query parameters
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = str(limit)

        async with httpx.AsyncClient() as client:
            url = f"{api_base}/buckets/{bucket_id}/events"
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            events = response.json()

        return {
            "bucket_id": bucket_id,
            "events": events,
            "count": len(events),
        }

    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            return {
                "error": f"Bucket '{bucket_id}' not found",
                "hint": "Use activitywatch://buckets to list available buckets",
            }
        return {
            "error": f"HTTP error: {error.response.status_code}",
        }

    except httpx.RequestError:
        return {
            "error": "Failed to fetch bucket events",
            "hint": "Ensure ActivityWatch is running and accessible",
        }
