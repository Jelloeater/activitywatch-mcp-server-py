"""ActivityWatch MCP Server - Query Help Prompts.

This module provides MCP prompts for guiding LLM interactions with ActivityWatch data.
Prompts are reusable message templates that help establish consistent patterns.
"""

from ..server import mcp


@mcp.prompt(
    name="ActivityWatch Query Help",
    description="Get help writing AQL queries for ActivityWatch data analysis",
)
def query_help(timeperiod: str = "today") -> str:
    """Generate a prompt for querying ActivityWatch data.

    Use this prompt when you need help writing AQL (ActivityWatch Query Language)
    queries to analyze time tracking data.

    Args:
        timeperiod: The time period to query (e.g., "today", "yesterday", "last 7 days")

    Returns:
        A prompt string guiding query creation
    """
    return f"""You are helping analyze ActivityWatch time tracking data.

Time period to analyze: {timeperiod}

## Available Data Types

ActivityWatch typically collects:

1. **afk** - Tracks when user is away from keyboard
2. **window** - Tracks active window titles and applications
3. **editor** - Tracks coding activity in editors (VSCode, etc.)
4. **browser** - Tracks browser tabs and URLs

## Common Query Patterns

```python
# Check if user was AFK
afk

# Get active window/app data
window

# Filter for specific app
window:firefox
window:code

# Combine conditions
afk == false and window:vscode

# Aggregate time by category
groups = window.groupby("app")
EVENT;
groups.sum(duration)
```

## Suggested Approach

1. First, use the `activitywatch-list-buckets` tool to see what data is available
2. Use the `activitywatch-get-events` tool to explore raw events
3. Use the `activitywatch-run-query` tool to execute AQL queries
4. Format queries as a single string with statements separated by semicolons

## Time Period Format

Time periods use ISO format:
- `2024-01-15/2024-01-16` for a specific day
- `2024-01-01/now` for from a date until now

Write your query now."""


@mcp.prompt(
    name="Daily Summary",
    description="Create a prompt for generating a daily time tracking summary",
)
def daily_summary(date: str = "today") -> str:
    """Generate a prompt for creating a daily summary of time tracking data.

    Use this prompt to analyze a day's worth of ActivityWatch data and create
    a comprehensive summary of productive time, app usage, and focus time.

    Args:
        date: The date to summarize (e.g., "today", "yesterday", "2024-01-15")

    Returns:
        A prompt string for generating a daily summary
    """
    return f"""You are analyzing ActivityWatch time tracking data for {date}.

Create a comprehensive daily summary including:

## Analysis Required

1. **Productive Time**: Identify time spent on work-related applications
2. **AFK Time**: Note periods when the user was away
3. **Top Applications**: List the most used apps and their durations
4. **Focus Time**: Identify deep work sessions (>30 min blocks)
5. **Breakdown**: Time by category (coding, meetings, browsing, etc.)

## Output Format

Provide a markdown summary with:
- Total tracked hours
- Breakdown by activity type
- Key productivity metrics
- Notable patterns or insights

Use these tools:
- `activitywatch-list-buckets` to discover available data
- `activitywatch-run-query` to analyze time periods
- `activitywatch-get-events` for detailed event inspection

Generate the summary now."""


@mcp.prompt(
    name="Analyze Time Period",
    description="Create a custom prompt for analyzing a specific time period",
)
def analyze_time_period(
    start_date: str = "today",
    end_date: str = "tomorrow",
    focus_area: str = "general productivity",
) -> str:
    """Generate a prompt for analyzing a specific time period.

    Use this prompt when you need to analyze ActivityWatch data for a custom
    date range and specific focus area.

    Args:
        start_date: Start of the analysis period (ISO format or relative like "yesterday")
        end_date: End of the analysis period (ISO format or relative like "today")
        focus_area: What to focus the analysis on (e.g., "coding", "meetings", "productivity")

    Returns:
        A prompt string for the analysis
    """
    return f"""You are analyzing ActivityWatch time tracking data from {start_date} to {end_date}.

Focus area: {focus_area}

## Analysis Goals

Based on the focus area, analyze:

### For "coding":
- Time spent in code editors (VSCode, etc.)
- Active coding vs idle time
- Languages or projects worked on

### For "meetings":
- Time marked as meeting (calendar integration if available)
- Focus time before/after meetings

### For "productivity":
- Deep work blocks (>1 hour of focused activity)
- Context switching patterns
- Peak productivity hours

### For "general":
- Overall time tracked
- Top applications and categories
- AFK patterns

## Approach

1. Query buckets using `activitywatch-list-buckets`
2. Execute appropriate AQL queries with `activitywatch-run-query`
3. Format results as actionable insights

## Time Period Format

Use ISO format for the API: `{start_date}T00:00:00+00:00/{end_date}T00:00:00+00:00`

Begin your analysis now."""
