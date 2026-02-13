"""ActivityWatch MCP Server - Main entry point."""

from .server import mcp


def main() -> None:
    """Run the ActivityWatch MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
