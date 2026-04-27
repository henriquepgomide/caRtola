.PHONY: help install aggregate viz test test-fast test-slow lint format clean

help:
	@echo "Available targets:"
	@echo "  install      - uv sync with dev + ui extras"
	@echo "  aggregate    - run the full aggregation pipeline"
	@echo "  viz          - launch Hamilton UI"
	@echo "  test         - run all tests (slow ones included)"
	@echo "  test-fast    - run all tests except those marked slow"
	@echo "  test-slow    - run only slow (real-data smoke) tests"
	@echo "  lint         - ruff check + mypy"
	@echo "  format       - ruff format + ruff check --fix"
	@echo "  clean        - remove pycache and other build artifacts"

install:
	uv sync --extra ui --group dev

aggregate:
	uv run cartola aggregate

viz:
	uv run cartola viz

test:
	uv run pytest -v

test-fast:
	uv run pytest -m "not slow" -v

test-slow:
	uv run pytest -m slow -v

lint:
	uv run ruff check src/cartola tests
	uv run mypy --ignore-missing-imports src/cartola

format:
	uv run ruff format src/cartola tests
	uv run ruff check --fix src/cartola tests

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
