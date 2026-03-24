"""ActivityWatch MCP Server - Buckets Resource.

This module provides MCP resources for accessing ActivityWatch bucket data.
Resources allow clients to read data without invoking tools.
"""

import httpx
from fastmcp import Context

from ..server import mcp


@mcp.resource(
    uri="activitywatch://buckets",
    name="ActivityWatch Buckets",
    description="Lists all ActivityWatch buckets with their metadata. Use this to discover available data sources before querying.",
)
async def buckets_resource(ctx: Context | None = None) -> str:
    """Fetch and return all ActivityWatch buckets as a resource.

    This resource provides a simple way to list all buckets without
    needing to invoke the list-buckets tool. Useful for discovery.

    Args:
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with bucket information
    """
    try:
        api_base = ctx.lifespan_context.get("api_base", "http://localhost:5600/api/0")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base}/buckets", timeout=10.0)
            response.raise_for_status()
            buckets_data = response.json()

        # Format as a simple list
        bucket_list = []
        for bucket_id, bucket_data in buckets_data.items():
            bucket_list.append({
                "id": bucket_id,
                "type": bucket_data.get("type", ""),
                "client": bucket_data.get("client", ""),
                "hostname": bucket_data.get("hostname", ""),
                "created": bucket_data.get("created", ""),
                "name": bucket_data.get("name"),
            })

        return {
            "buckets": bucket_list,
            "count": len(bucket_list),
        }

    except httpx.RequestError:
        return {
            "error": "Failed to fetch buckets",
            "hint": "Ensure ActivityWatch is running and accessible",
        }


@mcp.resource(
    uri="activitywatch://buckets/{bucket_type}",
    name="Buckets by Type",
    description="Lists ActivityWatch buckets filtered by type (e.g., 'afk', 'window', 'editor').",
)
async def buckets_by_type_resource(bucket_type: str, ctx: Context | None = None) -> str:
    """Fetch buckets filtered by type as a resource.

    Args:
        bucket_type: The bucket type to filter by (e.g., "afk", "window", "editor")
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with filtered bucket information
    """
    try:
        api_base = ctx.lifespan_context.get("api_base", "http://localhost:5600/api/0")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base}/buckets", timeout=10.0)
            response.raise_for_status()
            buckets_data = response.json()

        # Filter by type (case-insensitive)
        bucket_list = []
        for bucket_id, bucket_data in buckets_data.items():
            if bucket_type.lower() in bucket_data.get("type", "").lower():
                bucket_list.append({
                    "id": bucket_id,
                    "type": bucket_data.get("type", ""),
                    "client": bucket_data.get("client", ""),
                    "hostname": bucket_data.get("hostname", ""),
                    "created": bucket_data.get("created", ""),
                    "name": bucket_data.get("name"),
                })

        return {
            "filter": {"type": bucket_type},
            "buckets": bucket_list,
            "count": len(bucket_list),
        }

    except httpx.RequestError:
        return {
            "error": "Failed to fetch buckets",
            "hint": "Ensure ActivityWatch is running and accessible",
        }
