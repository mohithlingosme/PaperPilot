.PHONY: lint typecheck test-unit test-integration e2e build

lint:
	@if [ -f package.json ]; then npm run lint; else echo "No JS/TS project detected; skipping lint."; fi

typecheck:
	@if [ -f package.json ]; then npm run typecheck; else echo "No TypeScript config detected; skipping typecheck."; fi

test-unit:
	@if [ -f package.json ]; then npm run test:unit; else echo "No unit tests detected; skipping."; fi

test-integration:
	@if [ -f package.json ]; then npm run test:integration --if-present; else echo "No integration tests detected; skipping."; fi

e2e:
	@if [ -f package.json ]; then npm run test:e2e; else echo "No E2E tests detected; skipping."; fi

build:
	@if [ -f package.json ]; then npm run build; else echo "No build artifacts to produce; skipping."; fi
=======
# PaperPilot Development Makefile

# Tools
NODE ?= node
PYTHON ?= python
UV ?= uv
DOCKER_COMPOSE ?= docker-compose

.PHONY: setup dev test lint typecheck format build clean doctor db-up db-down db-reset migrate seed

# Setup development environment
setup:
	@echo "Setting up development environment..."
	@if [ -f package.json ]; then npm install; fi
	@if [ -f pyproject.toml ]; then $(UV) sync; fi
	@if [ -f docker-compose.yml ]; then $(DOCKER_COMPOSE) up -d; fi
	@echo "Setup complete. Run 'make doctor' to verify."

# Start development servers
dev:
	@echo "Starting development servers..."
	@if [ -f docker-compose.yml ]; then $(DOCKER_COMPOSE) up -d; fi
	@echo "Services started. Run individual apps manually or use scripts."

# Run all tests
test: test-unit test-integration

# Run unit tests
test-unit:
	@if [ -f package.json ]; then npm run test:unit; fi
	@if [ -f pyproject.toml ]; then $(UV) run pytest backend/app/tests/ -v --cov=backend/app --cov-report=term-missing; fi

# Run integration tests
test-integration:
	@if [ -f package.json ]; then npm run test:integration --if-present; fi
	@if [ -f pyproject.toml ]; then $(UV) run pytest backend/app/tests/ -k "integration" -v; fi

# Run E2E tests
e2e:
	@if [ -f package.json ]; then npm run test:e2e; fi

# Lint code
lint:
	@if [ -f package.json ]; then npm run lint; fi
	@if [ -f pyproject.toml ]; then $(UV) run ruff check .; fi

# Type check
typecheck:
	@if [ -f package.json ]; then npm run typecheck; fi
	@if [ -f pyproject.toml ]; then $(UV) run mypy backend/app; fi

# Format code
format:
	@if [ -f package.json ]; then npm run format; fi
	@if [ -f pyproject.toml ]; then $(UV) run black . && $(UV) run ruff check --fix .; fi

# Build artifacts
build:
	@if [ -f package.json ]; then npm run build; fi
	@if [ -f pyproject.toml ]; then echo "Python build not implemented yet"; fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@if [ -f package.json ]; then rm -rf dist/ build/; fi
	@if [ -f pyproject.toml ]; then rm -rf __pycache__/ *.pyc; fi

# Health check
doctor:
	@echo "Running health checks..."
	@scripts/doctor.sh

# Database management
db-up:
	$(DOCKER_COMPOSE) up -d postgres redis minio

db-down:
	$(DOCKER_COMPOSE) down

db-reset: db-down
	$(DOCKER_COMPOSE) up -d postgres redis minio
	@echo "Waiting for databases to be ready..."
	@sleep 10
	$(UV) run alembic upgrade head
	$(UV) run python scripts/seed.py

# Database migrations
migrate:
	$(UV) run alembic upgrade head

# Seed database
seed:
	$(UV) run python scripts/seed.py
