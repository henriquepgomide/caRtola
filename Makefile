FOLDER_PROJECT = src/cartola

.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@find . -type d -name '.mypy_cache' | xargs rm -rf
	@find . -type d -name '*.egg*' | xargs rm -rf
	@find . -type d -name '*.ropeproject' | xargs rm -rf
	@rm -rf src/build/
	@rm -rf src/dist/
	@rm -rf docs/build/
	@rm -rf references/
	@rm -rf results/
	@rm -f MANIFEST
	@rm -f .coverage.*


lint: ## lint files with ruff
	@poetry run ruff check --fix

mypy:
	@mypy --ignore-missing-imports --exclude download_data.py$$ --exclude __main__.py$$ --strict src/cartola

pre-commit:
	@pre-commit run --all-files

profile:
	@ydata_profiling -m -e $(args) report.html

docker-build:
	@kedro docker build --image cartola

docker-run:	
	@kedro docker run --image cartola

docker:
	$(MAKE) docker-build
	$(MAKE) docker-run
