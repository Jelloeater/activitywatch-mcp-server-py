"""ActivityWatch MCP Server - Resources package.

All resources are registered via the @mcp.resource decorator in their respective modules.
This package exports the resource functions primarily for testing purposes.
"""

from .buckets import buckets_resource
from .bucket_events import bucket_events_resource

__all__ = [
    "buckets_resource",
    "bucket_events_resource",
]
