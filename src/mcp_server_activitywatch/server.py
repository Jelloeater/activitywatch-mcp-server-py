"""ActivityWatch MCP Server - Core server implementation."""

import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import (
    get_events_handler,
    get_events_schema,
    get_settings_handler,
    get_settings_schema,
    list_buckets_handler,
    list_buckets_schema,
    query_examples_handler,
    query_examples_schema,
    run_query_handler,
    run_query_schema,
)


async def serve(api_base: str) -> None:
    """Run the ActivityWatch MCP server.

    Args:
        api_base: ActivityWatch API base URL (e.g. http://localhost:5600/api/0)
    """
    server = Server("mcp-activitywatch")

    # Print startup banner to stderr
    print("ActivityWatch MCP Server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("Version: 2.0.0", file=sys.stderr)
    print(f"API Endpoint: {api_base}", file=sys.stderr)
    print("Tools: activitywatch-list-buckets, activitywatch-run-query,", file=sys.stderr)
    print("       activitywatch-get-events, activitywatch-get-settings,", file=sys.stderr)
    print("       activitywatch-query-examples", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(
        "For help with query format, use 'activitywatch-query-examples' tool",
        file=sys.stderr,
    )
    print(file=sys.stderr)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available ActivityWatch tools."""
        return [
            Tool(
                name="activitywatch-list-buckets",
                description="List all ActivityWatch buckets with optional type filtering",
                inputSchema=list_buckets_schema(),
            ),
            Tool(
                name="activitywatch-query-examples",
                description="Get examples of properly formatted queries for the ActivityWatch MCP server",
                inputSchema=query_examples_schema(),
            ),
            Tool(
                name="activitywatch-run-query",
                description="Run a query in ActivityWatch's query language (AQL)",
                inputSchema=run_query_schema(),
            ),
            Tool(
                name="activitywatch-get-events",
                description="Get raw events from an ActivityWatch bucket",
                inputSchema=get_events_schema(),
            ),
            Tool(
                name="activitywatch-get-settings",
                description="Get ActivityWatch settings. Can retrieve all settings or a specific key if provided",
                inputSchema=get_settings_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls for ActivityWatch operations."""
        if name == "activitywatch-list-buckets":
            return await list_buckets_handler(api_base, arguments)
        elif name == "activitywatch-query-examples":
            return await query_examples_handler()
        elif name == "activitywatch-run-query":
            return await run_query_handler(api_base, arguments)
        elif name == "activitywatch-get-events":
            return await get_events_handler(api_base, arguments)
        elif name == "activitywatch-get-settings":
            return await get_settings_handler(api_base, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
