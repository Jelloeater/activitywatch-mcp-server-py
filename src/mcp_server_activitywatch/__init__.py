"""ActivityWatch MCP Server - Main entry point."""

import argparse
import asyncio
import os

from .server import serve


def main() -> None:
    """MCP ActivityWatch Server - Interact with ActivityWatch time tracking data."""
    parser = argparse.ArgumentParser(
        description="ActivityWatch MCP server - connect to your ActivityWatch time tracking data"
    )
    parser.add_argument(
        "--api-base",
        type=str,
        help="ActivityWatch API base URL (default: http://localhost:5600/api/0)",
    )

    args = parser.parse_args()

    # Get API base from args or environment variable
    api_base = args.api_base or os.getenv("AW_API_BASE", "http://localhost:5600/api/0")

    asyncio.run(serve(api_base))


if __name__ == "__main__":
    main()
