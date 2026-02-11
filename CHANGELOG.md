# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2024-02-10

### Added
- Complete Python rewrite from TypeScript
- Native UVX support for simplified deployment
- Model Context Protocol (MCP) server implementation
- 5 core tools: list-buckets, run-query, get-events, get-settings, query-examples
- Comprehensive error handling and validation
- Type hints throughout codebase
- Test suite with pytest

### Changed
- From TypeScript to Python 3.10+
- From npm/yarn to poetry package management
- From Docker-based deployment to UVX
- Improved API error messages and guidance

### Removed
- TypeScript implementation
- npm dependencies
- Docker container requirements

## [1.0.0] - 2024-01-15

### Added
- Initial TypeScript implementation
- Basic MCP server functionality
- ActivityWatch API integration
- CLI interface

[Unreleased]: https://github.com/8bitgentleman/activitywatch-mcp-server/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/8bitgentleman/activitywatch-mcp-server/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/8bitgentleman/activitywatch-mcp-server/releases/tag/v1.0.0