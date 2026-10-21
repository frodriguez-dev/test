# Development commands for the monorepo.
#
# Every target delegates to the existing tools: Docker Compose, uv, and pnpm.
# Override any variable on the command line, for example:
#   make up-build BACKEND_PORT=8080 FRONTEND_PORT=3000
#
# See DEPLOYING.md for prerequisites, environment setup, and troubleshooting.

SHELL := /bin/sh

COMPOSE ?= docker compose
COMPOSE_FILE ?= compose.yaml
COMPOSE_CMD = $(COMPOSE) -f $(COMPOSE_FILE)

BACKEND_SERVICE ?= backend
FRONTEND_SERVICE ?= frontend
DB_SERVICE ?= db

BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5173

BACKEND_DIR ?= backend
FRONTEND_DIR ?= frontend
BACKEND_ENV_FILE ?= .env

# Docker Compose reads these from the environment and falls back to the same
# defaults in compose.yaml.
export BACKEND_PORT FRONTEND_PORT

.DEFAULT_GOAL := help

.PHONY: help up up-build down down-volumes logs status health shell-backend \
	shell-frontend shell-db backend-install backend-migrate backend-dev \
	backend-test frontend-install frontend-dev frontend-build

help: ## Show the available targets and point to DEPLOYING.md
	@echo "Development commands for this repository"
	@echo
	@echo "Usage: make <target> [VARIABLE=value ...]"
	@echo
	@awk 'BEGIN {FS = ":.*## "; printf "Targets:\n"} \
		/^[a-zA-Z0-9_-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' \
		$(MAKEFILE_LIST)
	@echo
	@echo "Common overrides:"
	@echo "  BACKEND_PORT=8000     FRONTEND_PORT=5173"
	@echo "  BACKEND_SERVICE=backend  FRONTEND_SERVICE=frontend  DB_SERVICE=db"
	@echo "  COMPOSE=\"docker compose\"  COMPOSE_FILE=compose.yaml"
	@echo
	@echo "See DEPLOYING.md for prerequisites, environment setup, and troubleshooting."

# --- Docker Compose --------------------------------------------------------

up: ## Start the Docker Compose services in the background
	$(COMPOSE_CMD) up --detach

up-build: ## Build the images and start the services in the background
	$(COMPOSE_CMD) up --detach --build

down: ## Stop the services and keep PostgreSQL data
	$(COMPOSE_CMD) down

down-volumes: ## Stop the services and delete PostgreSQL data (destructive)
	$(COMPOSE_CMD) down --volumes

logs: ## Follow the logs of all Compose services
	$(COMPOSE_CMD) logs --follow

status: ## Show the status of the Compose services
	$(COMPOSE_CMD) ps

health: ## Check the backend health endpoint from the host
	@curl --fail --silent --show-error \
		"http://localhost:$(BACKEND_PORT)/api/health/"
	@echo

shell-backend: ## Open a shell in the backend container
	$(COMPOSE_CMD) exec $(BACKEND_SERVICE) sh

shell-frontend: ## Open a shell in the frontend container
	$(COMPOSE_CMD) exec $(FRONTEND_SERVICE) sh

shell-db: ## Open a psql session in the database container
	$(COMPOSE_CMD) exec $(DB_SERVICE) sh -c \
		'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# --- Backend without Docker ------------------------------------------------

backend-install: ## Install backend dependencies with uv
	cd $(BACKEND_DIR) && uv sync

backend-migrate: ## Apply Django migrations using backend/.env
	cd $(BACKEND_DIR) && \
		uv run --env-file $(BACKEND_ENV_FILE) manage.py migrate

backend-dev: ## Start the Django development server
	cd $(BACKEND_DIR) && \
		uv run --env-file $(BACKEND_ENV_FILE) manage.py runserver \
		127.0.0.1:$(BACKEND_PORT)

backend-test: ## Run the backend test suite using backend/.env
	cd $(BACKEND_DIR) && \
		uv run --env-file $(BACKEND_ENV_FILE) pytest

# --- Frontend without Docker -----------------------------------------------

frontend-install: ## Install frontend dependencies with pnpm
	cd $(FRONTEND_DIR) && pnpm install

frontend-dev: ## Start the Vite development server
	cd $(FRONTEND_DIR) && pnpm dev --port $(FRONTEND_PORT)

frontend-build: ## Type-check and build the frontend for production
	cd $(FRONTEND_DIR) && pnpm build

# --- Unknown targets -------------------------------------------------------

.DEFAULT:
	@echo "make: unknown target '$@'" >&2
	@echo "Run 'make help' to list the available targets." >&2
	@exit 1
