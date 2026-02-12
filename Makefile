# Makefile for ActivityWatch MCP Server

# Variables
PYTHON = python3
BUILD_DIR = src/mcp_server_activitywatch
UV = uv
UVX = uvx
COV_FAIL_UNDER = 80
COV_FAIL_UNDER_CLI = 40

# Default target
.DEFAULT_GOAL := test

# Phony targets
.PHONY: local default commit publish build install setup test clean format docs security install-hooks remove-hooks docker

# Single command for local development - runs format, lint, typecheck, security, and test
local: format lint typecheck security test

# Default target - runs all checks and tests
default: format security test

# Commit target - runs all actions for commit
dump: format security docs

# Publish target - runs security, build, and publish
publish: security build
	$(UV) publish

# Build target - builds the package
build: clean docs
	$(UV) build

# Install target - installs the package
install:
	$(UV) pip install . --upgrade

# Setup target - sets up development environment
setup:
	sudo apt-get install git-extras -y
	$(UV) pip install -e ".[dev]"

# Test target - runs tests with coverage (PyCharm compatible)
test:
	$(UV) run pytest --cov --cov-fail-under=$(COV_FAIL_UNDER) tests/
	$(UV) run pytest --cov --cov-fail-under=$(COV_FAIL_UNDER_CLI) tests/test_cli.py

# Clean target - cleans build artifacts and cache
clean:
	rm -rf dist
	rm -rf .mypy_cache
	$(UV) cache clean
	py3clean .

# Format target - formats code with ruff (Astral)
format:
	$(UV) run ruff check --fix $(BUILD_DIR)
	$(UV) run ruff format $(BUILD_DIR)

# Docs target - generates documentation
docs:
	rm -f CHANGELOG.md
	git-changelog -a -x >> CHANGELOG.md
	git add CHANGELOG.md
	rm -rf docs
	$(UV) run pdoc3 $(BUILD_DIR) -o docs -f
	$(UV) run pyreverse $(BUILD_DIR) -d docs
	$(UV) run mdformat docs
	$(UV) run mdToRst README.md >> ./docs/index.rst
	git add docs

# Security target - runs security checks
security:
	$(UV) run whispers $(BUILD_DIR)
	$(UV) run bandit --silent -r $(BUILD_DIR)

# Install hooks target - installs pre-commit hooks
install-hooks:
	$(UV) run pre-commit install

# Remove hooks target - removes pre-commit hooks
remove-hooks:
	$(UV) run pre-commit uninstall
	rm -rf .git/hooks

# Docker target - Docker commands (removed)
docker:
	@echo "Docker commands removed - using UV for deployment instead"

# Development targets
format-check:
	$(UV) run ruff check $(BUILD_DIR)
	$(UV) run ruff format --check $(BUILD_DIR)

lint:
	$(UV) run ruff check $(BUILD_DIR)

# Coverage targets
coverage:
	$(UV) run coverage run -m pytest tests/
	$(UV) run coverage report

# Type checking targets
typecheck:
	$(UV) run pyright $(BUILD_DIR)

# Help target - displays available targets
help:
	@echo "Available targets:"
	@echo "  local       - Run format, lint, typecheck, security, and tests (all local checks)"
	@echo "  default     - Run format, security, and tests"
	@echo "  dump        - Run format, security, and docs"
	@echo "  publish     - Publish to PyPI"
	@echo "  build       - Build the package"
	@echo "  install     - Install the package"
	@echo "  setup       - Setup development environment"
	@echo "  test        - Run tests with coverage (PyCharm compatible)"
	@echo "  clean       - Clean build artifacts and cache"
	@echo "  format      - Format code with ruff (Astral)"
	@echo "  docs        - Generate documentation"
	@echo "  security    - Run security checks (bandit, whispers)"
	@echo "  install-hooks - Install pre-commit hooks"
	@echo "  remove-hooks - Remove pre-commit hooks"
	@echo "  docker      - Docker commands (removed)"
	@echo "  format-check - Check code formatting with ruff (Astral)"
	@echo "  lint        - Run linting with ruff (Astral)"
	@echo "  coverage    - Generate coverage report"
	@echo "  typecheck   - Run type checking (pyright)"
	@echo "  help        - Display this help message"
