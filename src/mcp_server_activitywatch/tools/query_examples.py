"""ActivityWatch MCP Server - Query Examples Tool."""

from typing import Any

from mcp.types import TextContent
from pydantic import BaseModel


class QueryExamplesArgs(BaseModel):
    """Arguments for query_examples tool (no arguments needed)."""

    pass


def query_examples_schema() -> dict[str, Any]:
    """Return the JSON schema for query_examples tool."""
    return {"type": "object", "properties": {}}


async def query_examples_handler() -> list[TextContent]:
    """Get examples of properly formatted queries for the ActivityWatch MCP server.

    Returns:
        List of TextContent with query examples
    """
    examples = """
# ActivityWatch MCP Query Examples

Here are several examples of properly formatted queries for the ActivityWatch MCP server.

## CORRECT FORMAT

All queries must follow this structure:

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["events = query_bucket('aw-watcher-window_hostname'); RETURN = events;"]
}
```

Note that:
1. 'timeperiods' is an array with date ranges in the format "start/end"
2. 'query' is an array with a SINGLE STRING containing ALL statements
3. All query statements are in the same string, separated by semicolons

## COMMONLY USED QUERIES

### Get Active Window Events

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"]
}
```

### Get Active Window Events When Not AFK

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); afk_events = query_bucket(find_bucket('aw-watcher-afk_')); not_afk = filter_keyvals(afk_events, 'status', ['not-afk']); active_events = filter_period_intersect(window_events, not_afk); RETURN = active_events;"]
}
```

### Group Events by App

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); events_by_app = merge_events_by_keys(window_events, ['app']); RETURN = sort_by_duration(events_by_app);"]
}
```

### Filter by App Name

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); vscode_events = filter_keyvals(window_events, 'app', ['Code']); RETURN = vscode_events;"]
}
```

## COMMON ERRORS

### ❌ INCORRECT: Splitting query into multiple array items

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": [
    "window_events = query_bucket(find_bucket('aw-watcher-window_'));",
    "RETURN = window_events;"
  ]
}
```

### ❌ INCORRECT: Not wrapping query in an array

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": "window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"
}
```

### ❌ INCORRECT: Double-wrapping query in nested arrays

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": [[
    "window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"
  ]]
}
```

### ✅ CORRECT: Single string with all statements in an array

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"]
}
```

## NOTE FOR MCP CLIENT DEVELOPERS

If you're developing an MCP client that interacts with this server, be aware that:

1. The server expects `query` to be an array of strings
2. The server then transforms this to an array of arrays for the ActivityWatch API
3. Some MCP clients may inadvertently add extra array nesting
4. The server tries to automatically detect and handle these cases

Potential issues to watch for:
- The server transforming already-nested arrays (e.g., turning `[["query"]]` into `[[["query"]]]`)
- Error messages that don't match the actual issue

## INSTRUCTIONS FOR USERS

When asking an LLM to run a query using the 'activitywatch-run-query' tool in the ActivityWatch MCP server, use this format in your request:

"Please run this query with the 'activitywatch-run-query' tool:
- timeperiods: ['2024-10-28/2024-10-29']
- query: ['all statements go here in one string separated by semicolons; RETURN = results;']"

⚠️ Important: Make sure you explicitly tell the LLM to put ALL query statements in ONE string inside the array. Do not double-wrap the query in another array.

⚠️ If you consistently get errors about query format, try modifying your query to include explicit formatting instructions:

"Please run this query with the 'activitywatch-run-query' tool using EXACTLY this format:
{
  'timeperiods': ['2024-10-28/2024-10-29'],
  'query': ['all statements go here in one string separated by semicolons; RETURN = results;']
}"
"""

    return [TextContent(type="text", text=examples)]
