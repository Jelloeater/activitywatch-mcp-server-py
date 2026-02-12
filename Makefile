# Makefile for ActivityWatch MCP Server

# Variables
PYTHON = python3
BUILD_DIR = src/mcp_server_activitywatch
IMAGE_NAME = mcp-server-activitywatch
DOCKER_FILE = Dockerfile
POETRY = poetry
UV = uv
COV_FAIL_UNDER = 80
COV_FAIL_UNDER_CLI = 40

# Default target
.DEFAULT_GOAL := test

# Phony targets
.PHONY: default commit publish build install setup test clean format docs security install-hooks remove-hooks docker

# Default target - runs all checks and tests
default: format security test

# Commit target - runs all actions for commit
dump: format security docs

# Publish target - runs security, build, and publish
publish: security build
	$(POETRY) publish

# Build target - builds the package
build: clean docs
	$(POETRY) version $(shell git describe --tags --abbrev=0)
	git-changelog -p -a -x >> CHANGELOG.md
	git add CHANGELOG.md
	$(POETRY) build

# Install target - installs the package
install:
	$(UV) pip install . --upgrade

# Setup target - sets up development environment
setup:
	sudo apt-get install git-extras -y
	$(PYTHON) -m pip install pipx
	$(PYTHON) -m pipx ensurepath
	pipx install poetry
	$(POETRY) install

# Test target - runs tests with coverage
test:
	$(POETRY) run pytest --cov --cov-fail-under=$(COV_FAIL_UNDER) tests/
	$(POETRY) run pytest --cov --cov-fail-under=$(COV_FAIL_UNDER_CLI) tests/test_cli.py

# Clean target - cleans build artifacts and cache
clean:
	rm -rf dist
	rm -rf .mypy_cache
	$(POETRY) cache clear _default_cache --all  --no-interaction
	$(POETRY) cache clear PyPI --all  --no-interaction
	$(POETRY) check
	py3clean .

# Format target - formats code with isort, black, autoflake, and flake8
format:
	$(POETRY) run isort --atomic .
	$(POETRY) run black .
	$(POETRY) run autoflake $(BUILD_DIR)
	$(POETRY) run flake8 $(BUILD_DIR)

# Docs target - generates documentation
docs:
	rm -f CHANGELOG.md
	git-changelog -a -x >> CHANGELOG.md
	git add CHANGELOG.md
	rm -rf docs
	$(POETRY) run pdoc3 $(BUILD_DIR) -o docs -f
	$(POETRY) run pyreverse $(BUILD_DIR) -d docs
	$(POETRY) run mdformat docs
	$(POETRY) run mdToRst README.md >> ./docs/index.rst
	git add docs

# Security target - runs security checks
security:
	$(POETRY) run whispers $(BUILD_DIR)
	$(POETRY) run bandit --silent -r $(BUILD_DIR)

# Install hooks target - installs pre-commit hooks
install-hooks:
	$(POETRY) run pre-commit install

# Remove hooks target - removes pre-commit hooks
remove-hooks:
	$(POETRY) run pre-commit uninstall
	rm -rf .git/hooks

# Docker target - Docker commands (removed)
docker:
	@echo "Docker commands removed - using UV for deployment instead"

# Development targets
format-check:
	$(POETRY) run black --check .
	$(POETRY) run isort --check-only .
	$(POETRY) run flake8 $(BUILD_DIR)

lint:
	$(POETRY) run pylint $(BUILD_DIR)
	$(POETRY) run mypy $(BUILD_DIR)

# Coverage targets
coverage:
	$(POETRY) run coverage run -m pytest tests/
	$(POETRY) run coverage report

# Type checking targets
typecheck:
	$(POETRY) run mypy $(BUILD_DIR)

# Help target - displays available targets
help:
	@echo "Available targets:"
	@echo "  default     - Run format, security, and tests"
	@echo "  commit      - Run format, security, and docs"
	@echo "  publish     - Publish to PyPI"
	@echo "  build       - Build the package"
	@echo "  install     - Install the package"
	@echo "  setup       - Setup development environment"
	@echo "  test        - Run tests with coverage"
	@echo "  clean       - Clean build artifacts and cache"
	@echo "  format      - Format code with isort, black, autoflake, and flake8"
	@echo "  docs        - Generate documentation"
	@echo "  security    - Run security checks"
	@echo "  install-hooks - Install pre-commit hooks"
	@echo "  remove-hooks - Remove pre-commit hooks"
	@echo "  docker      - Docker commands (removed)"
	@echo "  format-check - Check code formatting"
	@echo "  lint        - Run linting tools"
	@echo "  coverage    - Generate coverage report"
	@echo "  typecheck   - Run type checking"
	@echo "  help        - Display this help message"
