"""ActivityWatch MCP Server - Run Query Tool."""

import json
from typing import Any

import httpx
from fastmcp import Context
from pydantic import BaseModel, Field

from ..server import mcp


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


@mcp.tool(name="activitywatch-run-query")
async def run_query(
    timeperiods: list[str],
    query: list[str],
    name: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Run a query in ActivityWatch's query language (AQL).

    Args:
        timeperiods: Time period(s) to query formatted as array of strings.
            For date ranges, use format: ['2024-10-28/2024-10-29']
        query: Array with ONE string containing ALL query statements separated by semicolons.
            DO NOT split statements into separate array elements.
        name: Optional name for the query (used for caching)
        ctx: MCP context with lifespan data containing api_base

    Returns:
        JSON string with query results
    """
    try:
        api_base = ctx.lifespan_context["api_base"] if ctx else "http://localhost:5600/api/0"

        # Process timeperiods to ensure correct format
        formatted_timeperiods = []

        # If we have exactly two timeperiods without slashes, combine them
        if len(timeperiods) == 2 and "/" not in timeperiods[0] and "/" not in timeperiods[1]:
            formatted_timeperiods.append(f"{timeperiods[0]}/{timeperiods[1]}")
        else:
            formatted_timeperiods = timeperiods.copy()

        # Format query - join all into single string (should already be one)
        query_string = " ".join(query)
        formatted_queries = [query_string]

        # Set up query data
        query_data = {"query": formatted_queries, "timeperiods": formatted_timeperiods}

        # Build URL with optional name parameter
        url = f"{api_base}/query/"
        if name:
            url += f"?name={name}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=query_data, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        return json.dumps(result, indent=2)

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Query failed: {error} (Status code: {status_code})"

        try:
            error_details = error.response.json()
            error_message += f"\nDetails: {json.dumps(error_details)}"
        except Exception:
            error_message += f"\nDetails: {error.response.text}"

        return error_message

    except httpx.RequestError as error:
        return f"Query failed: {error}"

    except Exception as error:
        return f"Query failed: {error}"
