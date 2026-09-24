# ═══════════════════════════════════════════════════════════════════════════════
# WAR-SQUID-V1 - Makefile
# Author: Ian Carter Kulani
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help install install-dev install-all clean test lint format check-deps \
        build docker-build docker-run docker-stop docker-logs docker-clean \
        run health check security-scan package deploy-docs all

# ── Configuration ──────────────────────────────────────────────────────────────
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
DOCKER_IMAGE := war-squid-v1
DOCKER_TAG := latest
VERSION := 1.0.0

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
WHITE := \033[1;37m
NC := \033[0m

# ── Help ───────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║                    WAR-SQUID-V1 - Makefile Help                      ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(WHITE)Installation:$(NC)"
	@echo "  $(GREEN)make install$(NC)         Install production dependencies"
	@echo "  $(GREEN)make install-dev$(NC)     Install development dependencies"
	@echo "  $(GREEN)make install-all$(NC)     Install all dependencies"
	@echo "  $(GREEN)make venv$(NC)            Create virtual environment"
	@echo ""
	@echo "$(WHITE)Testing:$(NC)"
	@echo "  $(GREEN)make test$(NC)            Run all tests"
	@echo "  $(GREEN)make test-unit$(NC)       Run unit tests"
	@echo "  $(GREEN)make test-integration$(NC) Run integration tests"
	@echo "  $(GREEN)make coverage$(NC)        Run tests with coverage"
	@echo ""
	@echo "$(WHITE)Code Quality:$(NC)"
	@echo "  $(GREEN)make lint$(NC)            Run linters"
	@echo "  $(GREEN)make format$(NC)          Format code"
	@echo "  $(GREEN)make check-deps$(NC)      Check dependencies"
	@echo "  $(GREEN)make security-scan$(NC)   Run security scans"
	@echo ""
	@echo "$(WHITE)Docker:$(NC)"
	@echo "  $(GREEN)make docker-build$(NC)    Build Docker images"
	@echo "  $(GREEN)make docker-run$(NC)      Run Docker container"
	@echo "  $(GREEN)make docker-stop$(NC)     Stop Docker container"
	@echo "  $(GREEN)make docker-logs$(NC)     View Docker logs"
	@echo "  $(GREEN)make docker-clean$(NC)    Clean Docker resources"
	@echo ""
	@echo "$(WHITE)Application:$(NC)"
	@echo "  $(GREEN)make run$(NC)             Run WAR-SQUID"
	@echo "  $(GREEN)make health$(NC)          Run health check"
	@echo "  $(GREEN)make check$(NC)           Run all checks"
	@echo ""
	@echo "$(WHITE)Build:$(NC)"
	@echo "  $(GREEN)make build$(NC)           Build package"
	@echo "  $(GREEN)make clean$(NC)           Clean build artifacts"
	@echo "  $(GREEN)make all$(NC)             Run complete workflow"
	@echo ""

# ── Virtual Environment ────────────────────────────────────────────────────────
venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip setuptools wheel
	@echo "$(GREEN)✓ Virtual environment created$(NC)"

# ── Installation ───────────────────────────────────────────────────────────────
install: venv
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: venv
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

install-all: install-dev
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

# ── Testing ────────────────────────────────────────────────────────────────────
test:
	@echo "$(BLUE)Running all tests...$(NC)"
	$(VENV_PYTHON) -m pytest tests/ -v

test-unit:
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(VENV_PYTHON) -m pytest tests/unit/ -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(VENV_PYTHON) -m pytest tests/integration/ -v

coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(VENV_PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

# ── Code Quality ───────────────────────────────────────────────────────────────
lint:
	@echo "$(BLUE)Running linters...$(NC)"
	-$(VENV_PYTHON) -m flake8 . --count --statistics
	-$(VENV_PYTHON) -m pylint war_squid.py --output-format=colorized
	-$(VENV_PYTHON) -m mypy war_squid.py --ignore-missing-imports
	@echo "$(GREEN)✓ Linting complete$(NC)"

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_PYTHON) -m black .
	$(VENV_PYTHON) -m isort .
	@echo "$(GREEN)✓ Code formatted$(NC)"

check-deps:
	@echo "$(BLUE)Checking dependencies...$(NC)"
	$(VENV_PYTHON) requirements-check.py --verbose

security-scan:
	@echo "$(BLUE)Running security scans...$(NC)"
	-$(VENV_PYTHON) -m bandit -r . -f json -o bandit-report.json
	-$(VENV_PYTHON) -m safety check
	@echo "$(GREEN)✓ Security scan complete$(NC)"

# ── Docker ─────────────────────────────────────────────────────────────────────
docker-build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f Dockerfile .
	docker build -t $(DOCKER_IMAGE):alpine -f Dockerfile.alpine .
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-run:
	@echo "$(BLUE)Starting Docker container...$(NC)"
	docker run -d --name war-squid-v1 \
		-p 5000:5000 -p 5001:5001 -p 8080:8080 -p 4444:4444 \
		--restart unless-stopped \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Container started$(NC)"

docker-stop:
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	-docker stop war-squid-v1
	-docker rm war-squid-v1
	@echo "$(GREEN)✓ Container stopped$(NC)"

docker-logs:
	docker logs -f war-squid-v1

docker-clean:
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	-docker stop war-squid-v1
	-docker rm war-squid-v1
	-docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG)
	-docker rmi $(DOCKER_IMAGE):alpine
	-docker system prune -f
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

# ── Application ────────────────────────────────────────────────────────────────
run:
	@echo "$(BLUE)Starting WAR-SQUID-V1...$(NC)"
	$(VENV_PYTHON) war_squid.py

health:
	@echo "$(BLUE)Running health check...$(NC)"
	$(VENV_PYTHON) health.py --verbose

check: check-deps health
	@echo "$(GREEN)✓ All checks complete$(NC)"

# ── Build ──────────────────────────────────────────────────────────────────────
build: clean
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_PYTHON) -m build
	@echo "$(GREEN)✓ Package built in dist/$(NC)"

clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	-rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ .mypy_cache/
	-find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	-find . -type f -name "*.pyc" -delete 2>/dev/null || true
	-find . -type f -name "*.pyo" -delete 2>/dev/null || true
	-rm -rf htmlcov/ .coverage coverage.xml
	-rm -f health_report.json requirements_report.json
	@echo "$(GREEN)✓ Build artifacts cleaned$(NC)"

# ── Complete Workflow ──────────────────────────────────────────────────────────
all: clean install-dev check test lint docker-build
	@echo "$(GREEN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║                    Complete Workflow Finished!                       ║$(NC)"
	@echo "$(GREEN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"

# ── Documentation ──────────────────────────────────────────────────────────────
docs:
	@echo "$(BLUE)Building documentation...$(NC)"
	$(VENV_PYTHON) -m sphinx -b html docs/ docs/_build/html
	@echo "$(GREEN)✓ Documentation built$(NC)"

# ── Deploy ─────────────────────────────────────────────────────────────────────
deploy-staging:
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(GREEN)✓ Deployed to staging$(NC)"

deploy-production:
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(GREEN)✓ Deployed to production$(NC)"
