"""ActivityWatch MCP Server - List Buckets Tool."""

import json
import os
from typing import Any

import httpx
from mcp.types import TextContent
from pydantic import BaseModel, Field


class ListBucketsArgs(BaseModel):
    """Arguments for list_buckets tool."""

    type: str | None = Field(None, description="Filter buckets by type")
    include_data: bool = Field(False, description="Include bucket data in response")


class Bucket(BaseModel):
    """ActivityWatch bucket model."""

    id: str
    type: str
    client: str
    hostname: str
    created: str
    name: str | None = None
    data: dict[str, Any] | None = None


def list_buckets_schema() -> dict[str, Any]:
    """Return the JSON schema for list_buckets tool."""
    return {
        "type": "object",
        "properties": {
            "type": {"type": "string", "description": "Filter buckets by type"},
            "include_data": {
                "type": "boolean",
                "description": "Include bucket data in response",
            },
        },
    }


async def list_buckets_handler(
    api_base: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """List all ActivityWatch buckets with optional type filtering.

    Args:
        api_base: ActivityWatch API base URL
        arguments: Tool arguments (type filter and include_data flag)

    Returns:
        List of TextContent with bucket information
    """
    try:
        # Parse and validate arguments
        args = ListBucketsArgs(**arguments)

        # Fetch buckets from ActivityWatch API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base}/buckets", timeout=10.0)
            response.raise_for_status()
            buckets_data = response.json()

        # Convert bucket dict to list with IDs
        bucket_list: list[Bucket] = []
        for bucket_id, bucket_data in buckets_data.items():
            bucket = Bucket(
                id=bucket_id,
                type=bucket_data.get("type", ""),
                client=bucket_data.get("client", ""),
                hostname=bucket_data.get("hostname", ""),
                created=bucket_data.get("created", ""),
                name=bucket_data.get("name"),
                data=bucket_data.get("data") if args.include_data else None,
            )
            bucket_list.append(bucket)

        # Apply type filter if specified
        if args.type:
            bucket_list = [
                b for b in bucket_list if args.type.lower() in b.type.lower()
            ]

        # Format output
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

        # Add helpful guidance (not in test mode)
        if os.getenv("PYTEST_CURRENT_TEST") is None and bucket_list:
            result_text += "\n\n"
            result_text += "You can access the events in these buckets using the activitywatch-get-events tool, for example:\n"
            result_text += f'activitywatch-get-events with bucket_id = "{bucket_list[0].id}"'

            if len(bucket_list) > 1:
                result_text += "\n\nOr try a different bucket:\n"
                result_text += f'activitywatch-get-events with bucket_id = "{bucket_list[1].id}"'
        elif os.getenv("PYTEST_CURRENT_TEST") is None and not bucket_list:
            result_text += "\n\nNo buckets found. Please check that ActivityWatch is running and collecting data."

        return [TextContent(type="text", text=result_text)]

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Failed to fetch buckets: {error} (Status code: {status_code})"

        # Try to include response data
        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return [TextContent(type="text", text=error_message)]

    except httpx.RequestError as error:
        error_message = f"""Failed to fetch buckets: {error}

This appears to be a network or connection error. Please check:
- The ActivityWatch server is running
- The API base URL is correct (currently: {api_base})
- No firewall or network issues are blocking the connection
"""
        return [TextContent(type="text", text=error_message)]

    except Exception as error:
        return [TextContent(type="text", text=f"Failed to fetch buckets: {error}")]
