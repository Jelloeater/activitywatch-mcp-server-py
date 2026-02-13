"""ActivityWatch MCP Server - Query Examples Tool."""

from ..server import mcp


@mcp.tool(name="activitywatch-query-examples")
async def query_examples() -> str:
    """Get examples of properly formatted queries for the ActivityWatch MCP server.

    This tool takes no parameters and returns helpful examples showing the correct
    format for ActivityWatch Query Language (AQL) queries.

    Returns:
        String with query examples and usage instructions
    """
    examples = """# ActivityWatch MCP Query Examples

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

### INCORRECT: Splitting query into multiple array items

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": [
    "window_events = query_bucket(find_bucket('aw-watcher-window_'));",
    "RETURN = window_events;"
  ]
}
```

### INCORRECT: Not wrapping query in an array

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": "window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"
}
```

### INCORRECT: Double-wrapping query in nested arrays

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": [[
    "window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"
  ]]
}
```

### CORRECT: Single string with all statements in an array

```json
{
  "timeperiods": ["2024-10-28/2024-10-29"],
  "query": ["window_events = query_bucket(find_bucket('aw-watcher-window_')); RETURN = window_events;"]
}
```

## INSTRUCTIONS FOR USERS

When asking an LLM to run a query using the 'activitywatch-run-query' tool in the ActivityWatch MCP server, use this format in your request:

"Please run this query with the 'activitywatch-run-query' tool:
- timeperiods: ['2024-10-28/2024-10-29']
- query: ['all statements go here in one string separated by semicolons; RETURN = results;']"

Important: Make sure you explicitly tell the LLM to put ALL query statements in ONE string inside the array. Do not double-wrap the query in another array.

If you consistently get errors about query format, try modifying your query to include explicit formatting instructions:

"Please run this query with the 'activitywatch-run-query' tool using EXACTLY this format:
{
  'timeperiods': ['2024-10-28/2024-10-29'],
  'query': ['all statements go here in one string separated by semicolons; RETURN = results;']
}"
"""

    return examples
