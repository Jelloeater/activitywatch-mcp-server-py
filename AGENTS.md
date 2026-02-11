# AGENTS.md - AI Agent Context for ActivityWatch MCP Server

This document provides context for AI agents (LLMs, coding assistants) working on this project. It contains architecture decisions, conventions, and guidance for future improvements.

## Project Overview

**Repository**: https://github.com/8bitgentleman/activitywatch-mcp-server  
**Purpose**: Model Context Protocol (MCP) server that connects LLMs to ActivityWatch time tracking API  
**Language**: Python 3.10+  
**Version**: 2.0.0 (migrated from TypeScript)  
**Package Name**: `mcp-server-activitywatch`  
**Entry Point**: `mcp-server-activitywatch` command

## Architecture

### High-Level Structure

```
┌─────────────────┐
│  MCP Client     │ (Claude Desktop, OpenCode, Crush)
│  (LLM)          │
└────────┬────────┘
         │ MCP Protocol (stdio)
         │
┌────────▼────────────────────────────────────────────┐
│  MCP Server (Python)                                │
│  ┌──────────────────────────────────────────────┐  │
│  │  server.py                                   │  │
│  │  - Stdio transport                           │  │
│  │  - Tool registration                         │  │
│  │  - Request routing                           │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  tools/                                      │  │
│  │  - list_buckets.py                           │  │
│  │  - run_query.py                              │  │
│  │  - get_events.py                             │  │
│  │  - get_settings.py                           │  │
│  │  - query_examples.py                         │  │
│  └──────────────────┬───────────────────────────┘  │
└───────────────────┬─┴────────────────────────────────┘
                    │ HTTP (httpx)
         ┌──────────▼──────────┐
         │  ActivityWatch API  │
         │  localhost:5600     │
         └─────────────────────┘
```

### Key Components

#### 1. Entry Point (`__init__.py`)
- Argument parsing for `--api-base` flag
- Environment variable support (`AW_API_BASE`)
- Default: `http://localhost:5600/api/0`
- Calls `serve()` from server.py

#### 2. Server (`server.py`)
- Initializes MCP server with stdio transport
- Registers 5 tools with decorators (`@server.list_tools()`, `@server.call_tool()`)
- Routes tool calls to appropriate handlers
- Prints startup banner to stderr

#### 3. Tools (`tools/*.py`)
Each tool follows this pattern:
- **Schema function**: Returns JSON schema for parameters
- **Handler function**: Async function that takes `api_base` and `arguments`
- **Returns**: `list[TextContent]` with results
- **Error handling**: Catches HTTP and network errors, returns helpful messages
- **Test mode detection**: Checks `PYTEST_CURRENT_TEST` env var to hide guidance text

### Data Flow

```
1. LLM calls tool → 2. MCP Protocol → 3. server.py routes to handler →
4. Handler makes HTTP request → 5. ActivityWatch API responds →
6. Handler formats response → 7. Returns TextContent → 8. LLM receives result
```

## Code Conventions

### Naming
- **Tool names**: Use hyphens (e.g., `activitywatch-list-buckets`)
- **Python modules**: Use underscores (e.g., `list_buckets.py`)
- **Functions**: Snake case (e.g., `get_events_handler`)
- **Classes**: Pascal case (e.g., `GetEventsArgs`)

### Type Hints
- All functions use type hints
- Use modern Python union syntax: `str | None` (not `Optional[str]`)
- Use `dict[str, Any]` for flexible dictionaries
- Use Pydantic `BaseModel` for parameter validation

### Error Handling
All tools follow this pattern:
```python
try:
    # Parse arguments
    args = ToolArgs(**arguments)
    
    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
    
    # Format and return
    return [TextContent(type="text", text=formatted_data)]

except httpx.HTTPStatusError as error:
    # Handle HTTP errors (4xx, 5xx)
    # Include status code and response details
    
except httpx.RequestError as error:
    # Handle network errors (connection refused, timeout)
    # Provide troubleshooting guidance
    
except Exception as error:
    # Catch-all for unexpected errors
```

### Testing
- Use pytest with pytest-asyncio
- Mock HTTP requests with pytest-httpx
- Test success cases AND error cases
- Use `conftest.py` to set `PYTEST_CURRENT_TEST` env var (suppresses guidance text)

### URL Encoding
- Always use `urllib.parse.quote(value, safe="")` for path parameters
- Use `urllib.parse.urlencode()` for query parameters
- This prevents issues with special characters (slashes, spaces, etc.)

## Current Implementation Details

### Tools

#### 1. `activitywatch-list-buckets`
**File**: `tools/list_buckets.py`  
**Purpose**: List all ActivityWatch buckets  
**Parameters**:
- `type` (optional): Filter by bucket type (case-insensitive)
- `include_data` (optional): Include bucket data in response

**API Call**: `GET {api_base}/buckets`  
**Returns**: Formatted list of buckets with IDs, types, clients, hostnames

#### 2. `activitywatch-run-query`
**File**: `tools/run_query.py`  
**Purpose**: Execute AQL (ActivityWatch Query Language) queries  
**Parameters**:
- `timeperiods`: Array of time period strings (e.g., `["2024-10-28/2024-10-29"]`)
- `query`: Array with ONE string containing ALL query statements separated by semicolons
- `name` (optional): Query name for caching

**API Call**: `POST {api_base}/query/`  
**Special handling**:
- Converts single date strings to proper ISO format with time
- Formats timeperiods as `["2024-10-28T00:00:00+00:00/2024-10-29T00:00:00+00:00"]`

**Common pitfall**: Users often split query statements into separate array elements. The tool expects ONE string with semicolons.

#### 3. `activitywatch-get-events`
**File**: `tools/get_events.py`  
**Purpose**: Get raw events from a specific bucket  
**Parameters**:
- `bucket_id`: Bucket identifier (required)
- `start` (optional): Start date/time (ISO format)
- `end` (optional): End date/time (ISO format)
- `limit` (optional): Max number of events

**API Call**: `GET {api_base}/buckets/{bucket_id}/events?{params}`  
**Special handling**:
- 404 errors provide helpful message about using `list-buckets` tool
- Uses `arguments.get("bucket_id")` in error handler to avoid unbound variable

#### 4. `activitywatch-get-settings`
**File**: `tools/get_settings.py`  
**Purpose**: Retrieve ActivityWatch settings  
**Parameters**:
- `key` (optional): Specific settings key to retrieve

**API Call**: 
- All settings: `GET {api_base}/settings`
- Specific key: `GET {api_base}/settings/{encoded_key}`

**Important**: Uses `urllib.parse.quote(key, safe="")` to properly encode keys with special characters

#### 5. `activitywatch-query-examples`
**File**: `tools/query_examples.py`  
**Purpose**: Provide query syntax reference  
**Parameters**: None  
**Returns**: Comprehensive examples of AQL queries with explanations

### Configuration

**Three configuration methods** (in order of precedence):
1. CLI flag: `--api-base http://custom:9999/api/1`
2. Environment variable: `AW_API_BASE=http://custom:9999/api/1`
3. Default: `http://localhost:5600/api/0`

All three methods are validated and working.

## Development Workflow

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/ -v                    # Run all tests
pytest tests/test_list_buckets.py   # Run specific test file
pytest --cov=src/                   # Run with coverage
```

### Type Checking
```bash
pyright src/
```
**Known issues**:
- `reportUnusedFunction` for decorated functions (false positive)
- Some type inference issues in dynamic data (acceptable)

### Linting
```bash
ruff check src/
ruff check --fix src/  # Auto-fix issues
```
**Known issues**:
- E501 line length warnings in documentation strings (acceptable for readability)

### Local Testing
```bash
# Test server startup
mcp-server-activitywatch

# Test with custom endpoint
mcp-server-activitywatch --api-base http://localhost:5600/api/0

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uvx mcp-server-activitywatch
```

## Future Improvements

### Priority: High

1. **Test with Real ActivityWatch Instance**
   - Currently all tests use mocked HTTP requests
   - Need integration tests against actual ActivityWatch server
   - Consider adding `tests/integration/` directory
   - Use `pytest.mark.integration` to separate from unit tests

2. **Add Get Events Tests**
   - File `tests/test_get_events.py` doesn't exist yet
   - Need tests for: success case, filtering, limit, errors
   - Follow pattern from `test_list_buckets.py`

3. **Publish to PyPI**
   - Package is ready but not published
   - Would enable `uvx mcp-server-activitywatch` without local installation
   - Need PyPI account and credentials
   - Update README with PyPI installation instructions

### Priority: Medium

4. **Add Query Validation**
   - AQL queries can be syntactically invalid
   - Consider adding basic validation before sending to API
   - Could improve error messages for common mistakes

5. **Add Caching Layer**
   - Repeated queries with same parameters could be cached
   - Would reduce load on ActivityWatch API
   - Consider TTL-based cache invalidation

6. **Add Bucket Autocomplete**
   - When `get-events` gets invalid bucket_id, suggest similar buckets
   - Could use fuzzy matching on available buckets

7. **Improve Time Period Parsing**
   - Current implementation in `run_query.py` is basic
   - Could support relative dates ("today", "yesterday", "last week")
   - Could validate date ranges

### Priority: Low

8. **Add More Query Examples**
   - `query_examples.py` has basic examples
   - Could add more advanced patterns (nested queries, filters, etc.)
   - Could categorize examples by use case

9. **Add Logging**
   - Currently no logging infrastructure
   - Could help with debugging production issues
   - Consider structured logging (JSON format)

10. **Add Rate Limiting**
    - Protect ActivityWatch API from too many requests
    - Could implement simple token bucket algorithm

11. **Add Response Streaming**
    - For large query results, could stream response
    - MCP supports streaming responses
    - Would improve UX for large datasets

12. **Add Health Check Tool**
    - New tool: `activitywatch-health-check`
    - Verify ActivityWatch server is accessible
    - Return version info, status, available watchers

## Known Issues

### Resolved
- ✅ URI encoding for settings keys with special characters (fixed in `get_settings.py`)
- ✅ All 15 tests passing
- ✅ Possible unbound variable in `get_events.py` error handler (fixed)

### Current
- ⚠️ Line length violations in documentation strings (E501 - acceptable)
- ⚠️ Pyright reports unused functions that are used via decorators (false positive)
- ⚠️ No integration tests against real ActivityWatch instance

### Won't Fix
- Query format confusion (documented extensively in README and examples tool)

## Migration Notes (TypeScript → Python)

**Date**: 2024-02-10  
**Reason**: Better Python ecosystem integration, simpler deployment via UVX

### What Changed
- Complete rewrite in Python
- httpx instead of axios
- Pydantic instead of Zod
- pytest instead of Jest
- Async/await patterns similar to TypeScript
- Tool naming: underscores → hyphens

### What Stayed the Same
- All 5 tools with identical functionality
- API endpoints and parameters
- Error handling patterns
- Response formatting

### Breaking Changes
- Tool names now use hyphens (e.g., `activitywatch-list-buckets` instead of `activitywatch_list_buckets`)
- Installation method changed (npm → uvx/pip)
- Configuration file format unchanged (same JSON for MCP clients)

## Tips for AI Agents

### When Adding New Tools
1. Create `tools/new_tool.py`
2. Implement schema function and async handler
3. Register in `server.py` (two places: list_tools and call_tool)
4. Create `tests/test_new_tool.py` with success and error cases
5. Update README with tool documentation
6. Update this AGENTS.md with implementation details

### When Fixing Bugs
1. Write a failing test first
2. Fix the implementation
3. Verify all tests pass
4. Check with pyright and ruff
5. Update documentation if behavior changes

### When Refactoring
1. Ensure all tests pass before starting
2. Make small, incremental changes
3. Run tests after each change
4. Keep test coverage at 100%
5. Update this file if architecture changes

### Common Pitfalls
- Forgetting to URL-encode path parameters → Use `quote(value, safe="")`
- Not handling network errors → Always catch `httpx.RequestError`
- Including line numbers in oldString when editing → Strip them first
- Forgetting to update both list_tools AND call_tool in server.py
- Not checking PYTEST_CURRENT_TEST before adding guidance text

## Resources

### Documentation
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- ActivityWatch API: https://docs.activitywatch.net/en/latest/api.html
- httpx: https://www.python-httpx.org/
- Pydantic: https://docs.pydantic.dev/

### Related Projects
- ActivityWatch: https://github.com/ActivityWatch/activitywatch
- MCP Servers: https://github.com/modelcontextprotocol/servers
- Other MCP implementations: https://glama.ai/mcp/servers

## Contact

**Repository Owner**: 8bitgentleman  
**Repository**: https://github.com/8bitgentleman/activitywatch-mcp-server  
**Issues**: https://github.com/8bitgentleman/activitywatch-mcp-server/issues

---

Last Updated: 2024-02-10  
Version: 2.0.0  
For questions or updates, create an issue in the repository.
