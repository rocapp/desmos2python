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
clean: clean-build clean-pyc clean-nox clean-coverage clean-pytest clean-docs-build

.PHONY: prebuild
prebuild: clean
	@echo "+ $@"
	@/usr/bin/env bash -c './scripts/prebuild.sh'

.PHONY: build
build: prebuild ## Package release
	@echo "+ $@"
	@/usr/bin/env bash -c './scripts/build.sh'

.PHONY: test
test: build ## run tests
	@echo "+ $@"
	pytest

.PHONY: release-pypi
release-pypi: ## Package and upload release to pypi
	@echo "+ $@"
	@/bin/bash -c 'twine upload dist/*'

.PHONY: release-github
release-github: build ## Package and upload release to github
	@echo "+ $@"
	@/bin/bash -c 'gh release create'

.PHONY: tag
tag:
ifndef tag_version
	@echo "+ $@"
	@echo "Enter a tag version: "
	@read tag_version; if [ $$tag_version ]; then git tag $$tag_version ; fi
endif

.PHONY: release
release: clean tag build release-pypi release-github
	@echo "+ $@"
	@echo "...done with all release tasks."

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
