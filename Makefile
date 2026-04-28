help: ## display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## set up local environment
	@set -e && \
	uv sync --extra ui --group dev && \
	uv run pre-commit install && \
	uv run pre-commit install --hook-type commit-msg

aggregate: ## run the full aggregation pipeline
	@uv run cartola aggregate

viz: ## launch Hamilton UI
	@uv run cartola viz

test: ## run all tests (slow ones included)
	@uv run pytest

test-fast: ## run all tests except those marked slow
	@uv run pytest -m "not slow"

test-slow: ## run only slow (real-data smoke) tests
	@uv run pytest -m slow

lint: ## lint + format the code
	@uv run ruff check --fix

pre-commit: ## run pre-commit hooks
	@uv run pre-commit run --all-files

clean: ## remove build artifacts
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@rm -f .coverage coverage.xml report.xml
