"""ActivityWatch MCP Server - FastMCP implementation."""

import argparse
import os
import sys
from typing import Any

from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan


@lifespan
async def app_lifespan(server: FastMCP) -> Any:
    """Application lifespan managing api_base configuration.

    Parses command line arguments and environment variables to configure
    the ActivityWatch API base URL, then yields it in the context.
    """
    parser = argparse.ArgumentParser(
        description="ActivityWatch MCP server - connect to your ActivityWatch time tracking data"
    )
    parser.add_argument(
        "--api-base",
        type=str,
        help="ActivityWatch API base URL (default: http://localhost:5600/api/0)",
    )

    args = parser.parse_args()
    api_base = args.api_base or os.getenv("AW_API_BASE", "http://localhost:5600/api/0")

    # Print startup banner to stderr
    print("ActivityWatch MCP Server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("Version: 2.1.0 (FastMCP)", file=sys.stderr)
    print(f"API Endpoint: {api_base}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(
        "For help with query format, use 'activitywatch-query-examples' tool",
        file=sys.stderr,
    )
    print(file=sys.stderr)

    yield {"api_base": api_base}


# Create FastMCP instance with lifespan
mcp = FastMCP(
    "ActivityWatch",
    lifespan=app_lifespan,
)

# Import tools to register them via decorators
from .tools import (  # noqa: E402
    list_buckets,
    get_events,
    run_query,
    get_settings,
    query_examples,
)

__all__ = ["mcp"]
