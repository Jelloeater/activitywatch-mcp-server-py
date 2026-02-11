"""ActivityWatch MCP Server - Run Query Tool."""

import json
from typing import Any

import httpx
from mcp.types import TextContent
from pydantic import BaseModel, Field


class RunQueryArgs(BaseModel):
    """Arguments for run_query tool."""

    timeperiods: list[str] = Field(
        ...,
        description="Time periods in format ['2024-10-28/2024-10-29']",
        min_length=1,
        max_length=10,
    )
    query: list[str] = Field(
        ...,
        description="MUST BE A SINGLE STRING with all statements separated by semicolons",
        min_length=1,
        max_length=1,
    )
    name: str | None = Field(None, description="Optional query name for caching")


def run_query_schema() -> dict[str, Any]:
    """Return the JSON schema for run_query tool."""
    return {
        "type": "object",
        "properties": {
            "timeperiods": {
                "type": "array",
                "description": "Time periods to query. Format: ['2024-10-28/2024-10-29'] where dates are in ISO format and joined with a slash",
                "items": {
                    "type": "string",
                    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}/[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                    "description": "Time period in format 'start-date/end-date'",
                },
                "minItems": 1,
                "maxItems": 10,
            },
            "query": {
                "type": "array",
                "description": "MUST BE A SINGLE STRING containing all query statements separated by semicolons. DO NOT split into multiple strings.",
                "items": {
                    "type": "string",
                    "description": "Complete query with all statements in one string separated by semicolons",
                },
                "minItems": 1,
                "maxItems": 1,
            },
            "name": {
                "type": "string",
                "description": "Optional name for the query (used for caching)",
            },
        },
        "required": ["timeperiods", "query"],
    }


async def run_query_handler(api_base: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Run a query in ActivityWatch's query language.

    Args:
        api_base: ActivityWatch API base URL
        arguments: Tool arguments (timeperiods, query, and optional name)

    Returns:
        List of TextContent with query results
    """
    try:
        # Parse and validate arguments
        args = RunQueryArgs(**arguments)

        # Process timeperiods to ensure correct format
        formatted_timeperiods = []

        # If we have exactly two timeperiods without slashes, combine them
        if (
            len(args.timeperiods) == 2
            and "/" not in args.timeperiods[0]
            and "/" not in args.timeperiods[1]
        ):
            formatted_timeperiods.append(f"{args.timeperiods[0]}/{args.timeperiods[1]}")
        else:
            # Use timeperiods as provided
            formatted_timeperiods = args.timeperiods.copy()

        # Format query - join all into single string (should already be one)
        query_string = " ".join(args.query)
        formatted_queries = [query_string]

        # Set up query data
        query_data = {"query": formatted_queries, "timeperiods": formatted_timeperiods}

        # Build URL with optional name parameter
        url = f"{api_base}/query/"
        if args.name:
            url += f"?name={args.name}"

        # Make the request to the ActivityWatch query endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=query_data, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        # Format response
        response_text = json.dumps(result, indent=2)

        return [TextContent(type="text", text=response_text)]

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Query failed: {error} (Status code: {status_code})"

        # Try to include response data
        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return [TextContent(type="text", text=error_message)]

    except httpx.RequestError as error:
        error_message = f"Query failed: {error}"
        return [TextContent(type="text", text=error_message)]

    except Exception as error:
        return [TextContent(type="text", text=f"Query failed: {error}")]
