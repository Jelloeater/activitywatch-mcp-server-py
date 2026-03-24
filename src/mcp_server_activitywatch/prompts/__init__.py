"""ActivityWatch MCP Server - Prompts package.

All prompts are registered via the @mcp.prompt decorator in their respective modules.
This package exports the prompt functions primarily for testing purposes.
"""

from .query_help import query_help, daily_summary, analyze_time_period

__all__ = [
    "query_help",
    "daily_summary",
    "analyze_time_period",
]
