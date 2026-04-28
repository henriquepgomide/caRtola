.PHONY: help install aggregate viz test test-fast test-slow lint format clean

help: ## display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:
	@set -e && \
	uv sync --extra ui --group dev && \
	uv run pre-commit install && \
	uv run pre-commit install --hook-type commit-msg

aggregate:
	uv run cartola aggregate

viz:
	uv run cartola viz

test:
	uv run pytest

test-fast:
	uv run pytest -m "not slow"

test-slow:
	uv run pytest -m slow

lint:
	uv run ruff check --fix

pre-commit:
	uv run pre-commit run --all-files

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@rm -f .coverage coverage.xml report.xml
