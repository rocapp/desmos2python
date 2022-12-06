.PHONY: clean-tox
clean-tox: ## Remove tox testing artifacts
	@echo "+ $@"
	@rm -rf .tox/

.PHONY: clean-nox
clean-nox: ## Remove nox testing artifacts
	@echo "+ $@"
	@rm -rf .nox/

.PHONY: clean-coverage
clean-coverage: ## Remove coverage reports
	@echo "+ $@"
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf coverage.xml

.PHONY: clean-pytest
clean-pytest: ## Remove pytest cache
	@echo "+ $@"
	@rm -rf .pytest_cache/

.PHONY: clean-docs-build
clean-docs-build: ## Remove local docs
	@echo "+ $@"
	@rm -rf docs/_build

.PHONY: clean-build
clean-build: ## Remove build artifacts
	@echo "+ $@"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@rm -f *.deb
	@rm -f .local-bashrc

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "+ $@"
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

.PHONY: clean ## Remove all file artifacts
clean: clean-tox clean-build clean-pyc clean-nox clean-coverage clean-pytest clean-docs-build

.PHONY: lint
lint: ## Check code style
	@echo "+ $@"
	@tox -e lint

.PHONY: test
test: ## Run tests quickly with the default Python
	@echo "+ $@"
	@tox -e test

.PHONY: test-all
test-all: ## Run tests on every Python version with tox
	@echo "+ $@"
	@tox -r -e test -e qa

.PHONY: build
build: clean ## Package and upload release
	@echo "+ $@"
	@./build.sh

.PHONY: release
release: build ## Package and upload release
	@echo "+ $@"
	@./deploy.sh

.PHONY: sdist
sdist: clean ## Build sdist distribution
	@echo "+ $@"
	@python -m build --sdist
	@ls -l dist

.PHONY: wheel
wheel: clean ## Build wheel distribution
	@echo "+ $@"
	@python -m build --wheel
	@ls -l dist

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
