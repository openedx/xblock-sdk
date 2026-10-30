# Equivalent to setting all targets .PHONY
MAKEFLAGS += --always-make

# Generates a help message. Borrowed from https://github.com/pydanny/cookiecutter-djangopackage.
help: ## display this help message
	@echo "Please use \`make <target>\` where <target> is one of"
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

install_frontend_prereqs:
	cd frontend && pnpm install

install_backend_prereqs:
	uv sync

install_prereqs: install_frontend_prereqs install_backend_prereqs ## Install prerequisites for development

build: ## Build the frontend packages
	cd frontend && pnpm run build

build.watch: ## Watch and automatically rebuild the frontend when source files change
	cd frontend && pnpm run build:watch

upgrade.frontend: ## Upgrade frontend packages
	cd frontend && pnpm upgrade

upgrade.backend:
	uv sync --upgrade

upgrade: upgrade.frontend upgrade.backend ## Upgrade all dependencies

format.frontend:
	cd frontend && pnpm run format

format.backend:
	uv run ruff format

format: format.frontend format.backend ## Format code in this repository

lint.frontend:
	cd frontend && pnpm run lint

lint.backend:
	uv run ruff check

lint: lint.frontend lint.backend ## Lint the code in this repository

lint.fix.frontend:
	cd frontend && pnpm run lint:fix

lint.fix.backend:
	uv run ruff check --fix

lint.fix: lint.fix.frontend lint.fix.backend ## Automatically fix linter issues in this repository

quality.backend: lint.backend
	uv run ruff format --check

quality.frontend: lint.frontend

quality: quality.backend quality.frontend ## Run all quality checks

test.backend:
	uv run pytest

test.frontend:
	cd frontend && pnpm run test

test: test.backend test.frontend ## Run automated tests
