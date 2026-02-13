"""ActivityWatch MCP Server - List Buckets Tool."""

import json
import os
from typing import Any

import httpx
from fastmcp import Context
from pydantic import BaseModel, Field

from ..server import mcp


class Bucket(BaseModel):
    """ActivityWatch bucket model."""

    id: str
    type: str
    client: str
    hostname: str
    created: str
    name: str | None = None
    data: dict[str, Any] | None = None


@mcp.tool(name="activitywatch-list-buckets")
async def list_buckets(
    type: str | None = None,
    include_data: bool = False,
    ctx: Context | None = None,
) -> str:
    """List all ActivityWatch buckets with optional type filtering.

    Args:
        type: Filter buckets by type (e.g., "window", "web", "afk")
        include_data: Include bucket data in response
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with bucket information
    """
    try:
        api_base = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base}/buckets", timeout=10.0)
            response.raise_for_status()
            buckets_data = response.json()

        bucket_list: list[Bucket] = []
        for bucket_id, bucket_data in buckets_data.items():
            bucket = Bucket(
                id=bucket_id,
                type=bucket_data.get("type", ""),
                client=bucket_data.get("client", ""),
                hostname=bucket_data.get("hostname", ""),
                created=bucket_data.get("created", ""),
                name=bucket_data.get("name"),
                data=bucket_data.get("data") if include_data else None,
            )
            bucket_list.append(bucket)

        if type:
            bucket_list = [b for b in bucket_list if type.lower() in b.type.lower()]

        formatted_buckets = [
            {
                "id": b.id,
                "type": b.type,
                "client": b.client,
                "hostname": b.hostname,
                "created": b.created,
                "name": b.name,
                **({"data": b.data} if b.data else {}),
            }
            for b in bucket_list
        ]

        result_text = json.dumps(formatted_buckets, indent=2)

        if os.getenv("PYTEST_CURRENT_TEST") is None and bucket_list:
            result_text += "\n\n"
            result_text += (
                "You can access the events in these buckets using the activitywatch-get-events tool, for example:\n"
            )
            result_text += f'activitywatch-get-events with bucket_id = "{bucket_list[0].id}"'

            if len(bucket_list) > 1:
                result_text += "\n\nOr try a different bucket:\n"
                result_text += f'activitywatch-get-events with bucket_id = "{bucket_list[1].id}"'
        elif os.getenv("PYTEST_CURRENT_TEST") is None and not bucket_list:
            result_text += "\n\nNo buckets found. Please check that ActivityWatch is running and collecting data."

        return result_text

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch buckets: {error} (Status code: {status_code})"

        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return error_message

    except httpx.RequestError as error:
        api_base_display = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"
        return f"""Failed to fetch buckets: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running
- The API base URL is correct (currently: {api_base_display})
- No firewall or network issues are blocking the connection
"""

    except Exception as error:
        return f"Failed to fetch buckets: {error}"
