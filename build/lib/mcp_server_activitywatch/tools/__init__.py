"""ActivityWatch MCP Server - Tools package.

All tools are registered via the @mcp.tool decorator in their respective modules.
This package exports the tool functions primarily for testing purposes.
"""

from .get_events import get_events
from .get_settings import get_settings
from .list_buckets import list_buckets
from .query_examples import query_examples
from .run_query import run_query

__all__ = [
    "get_events",
    "get_settings",
    "list_buckets",
    "query_examples",
    "run_query",
]
