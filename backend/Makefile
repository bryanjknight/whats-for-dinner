.PHONY: help install install-dev build validate test test-cov test-fast test-unit test-integration test-watch lint format check-format type-check clean all ci dev info

PYTHON := python3
VENV := ../.venv
export PATH := $(VENV)/bin:$(PATH)

# Color output
BOLD := \033[1m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m # No Color

help: ## Display this help message
	@echo "$(BOLD)Meal Planner Backend - Build Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)Common workflows:$(NC)"
	@echo "  make build validate test      # Full validation and test pipeline"
	@echo "  make install-dev              # Setup dev environment"
	@echo "  make all                      # Full CI pipeline (clean + build + validate + test)"

info: ## Show tool paths and versions
	@echo "$(BOLD)Environment Info$(NC)"
	@echo "  Python:   $$(which python)"
	@echo "  Ruff:     $$(which ruff)"
	@echo "  MyPy:     $$(which mypy)"
	@echo "  PyTest:   $$(which pytest)"
	@echo ""
	@echo "$(BOLD)Versions$(NC)"
	@echo "  Python:   $$(python --version)"
	@echo "  Ruff:     $$(ruff --version)"
	@echo "  MyPy:     $$(mypy --version)"
	@echo "  PyTest:   $$(pytest --version)"

.DEFAULT_GOAL := help

# Installation targets
install: ## Install production dependencies
	$(PYTHON) -m pip install -e . --quiet
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies (includes production)
	$(PYTHON) -m pip install -e ".[dev]" --quiet
	@echo "$(GREEN)✓ Dev dependencies installed$(NC)"

# Build target
build: install-dev ## Build and prepare project
	@echo "$(GREEN)✓ Build complete$(NC)"

# Validation targets
validate: lint type-check ## Run all validation checks

lint: ## Check code style with ruff
	@echo "$(BOLD)Linting with ruff...$(NC)"
	ruff check app tests --show-fixes
	@echo "$(GREEN)✓ Linting passed$(NC)"

format: ## Format code with ruff
	@echo "$(BOLD)Formatting with ruff...$(NC)"
	ruff format app tests
	@echo "$(GREEN)✓ Formatting complete$(NC)"

check-format: ## Check if code is formatted
	@echo "$(BOLD)Checking code format...$(NC)"
	ruff format --check app tests
	@echo "$(GREEN)✓ Code is properly formatted$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BOLD)Type checking with mypy...$(NC)"
	mypy app --strict
	@echo "$(GREEN)✓ Type checking passed$(NC)"

# Test targets
test: ## Run tests
	@echo "$(BOLD)Running tests...$(NC)"
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BOLD)Running tests with coverage...$(NC)"
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests passed - Coverage report: htmlcov/index.html$(NC)"

test-fast: ## Run tests without coverage
	@echo "$(BOLD)Running tests (fast)...$(NC)"
	pytest tests/ -q

test-unit: ## Run only unit tests
	@echo "$(BOLD)Running unit tests...$(NC)"
	pytest tests/ -v -m unit

test-integration: ## Run only integration tests
	@echo "$(BOLD)Running integration tests...$(NC)"
	pytest tests/ -v -m integration

test-watch: ## Run tests on file changes (requires pytest-watch)
	@echo "$(BOLD)Watching for changes...$(NC)"
	ptw tests/ -v

# Cleanup targets
clean: ## Clean build artifacts and cache
	@echo "$(BOLD)Cleaning...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Full pipeline targets
all: clean install-dev validate test ## Run complete build pipeline (clean, install, validate, test)

ci: install-dev check-format lint type-check test-cov ## Run CI pipeline (no clean, for CI systems)

dev: install-dev format ## Setup development environment with formatted code
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "  Tips:"
	@echo "    make test         # Run tests"
	@echo "    make validate     # Run validation checks"
	@echo "    make test-cov     # Run tests with coverage"
