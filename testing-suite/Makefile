# Makefile for testing suite

# Variables
PROJECT_NAME = enterprise-testing-suite
RESULTS_DIR = results
REPORTS_DIR = reports
DOCKER_COMPOSE = docker-compose.yml

# Default target
.PHONY: help
help:
	@echo "Enterprise Testing Suite - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup              Install dependencies"
	@echo "  make test               Run all tests"
	@echo "  make test-unit          Run unit tests"
	@echo "  make test-integration   Run integration tests"
	@echo "  make test-e2e           Run end-to-end tests"
	@echo "  make test-api           Run API tests"
	@echo "  make test-security      Run security tests"
	@echo "  make test-performance   Run performance tests"
	@echo "  make test-database      Run database tests"
	@echo "  make test-accessibility Run accessibility tests"
	@echo "  make test-chaos         Run chaos engineering tests"
	@echo "  make test-coverage      Run tests with coverage"
	@echo "  make clean              Clean test results"
	@echo "  make docker-setup       Setup Docker environment"
	@echo "  make docker-test        Run tests in Docker"
	@echo "  make report             Generate test reports"
	@echo "  make lint               Run code linting"
	@echo "  make lint-fix           Fix linting issues"

# Setup dependencies
.PHONY: setup
setup:
	npm install
	pip3 install -r requirements.txt
	mkdir -p $(RESULTS_DIR) $(REPORTS_DIR)

# Clean test results
.PHONY: clean
clean:
	rm -rf $(RESULTS_DIR)/*
	rm -rf $(REPORTS_DIR)/*
	mkdir -p $(RESULTS_DIR) $(REPORTS_DIR)

# Run all tests
.PHONY: test
test: test-unit test-integration test-api test-regression

# Run unit tests
.PHONY: test-unit
test-unit:
	npm run test:unit

# Run integration tests
.PHONY: test-integration
test-integration:
	npm run test:integration

# Run smoke tests
.PHONY: test-smoke
test-smoke:
	npm run test:smoke

# Run end-to-end tests
.PHONY: test-e2e
test-e2e:
	npm run test:e2e

# Run API tests
.PHONY: test-api
test-api:
	npm run test:api

# Run security tests
.PHONY: test-security
test-security:
	npm run test:security

# Run performance tests
.PHONY: test-performance
test-performance:
	npm run test:performance

# Run regression tests
.PHONY: test-regression
test-regression:
	npm run test:regression

# Run database tests
.PHONY: test-database
test-database:
	npm run test:database

# Run configuration tests
.PHONY: test-config
test-config:
	npm run test:config

# Run accessibility tests
.PHONY: test-accessibility
test-accessibility:
	npm run test:accessibility

# Run chaos engineering tests
.PHONY: test-chaos
test-chaos:
	npm run test:chaos

# Run tests with coverage
.PHONY: test-coverage
test-coverage:
	npm run test:coverage

# Generate test reports
.PHONY: report
report:
	npm run report

# Run code linting
.PHONY: lint
lint:
	npm run lint

# Fix linting issues
.PHONY: lint-fix
lint-fix:
	npm run lint:fix

# Setup Docker environment
.PHONY: docker-setup
docker-setup:
	docker-compose -f $(DOCKER_COMPOSE) up -d postgres mysql mongodb redis selenium-hub chrome firefox mock-api

# Run tests in Docker
.PHONY: docker-test
docker-test: docker-setup
	docker-compose -f $(DOCKER_COMPOSE) run test-runner npm test

# Stop Docker environment
.PHONY: docker-stop
docker-stop:
	docker-compose -f $(DOCKER_COMPOSE) down

# View Docker logs
.PHONY: docker-logs
docker-logs:
	docker-compose -f $(DOCKER_COMPOSE) logs -f

# Run specific test category in Docker
.PHONY: docker-test-%
docker-test-%:
	docker-compose -f $(DOCKER_COMPOSE) run test-runner npm run test:$(subst docker-test-,,$@)

# Generate coverage report
.PHONY: coverage-report
coverage-report:
	npm run test:coverage
	@echo "Coverage report generated in $(RESULTS_DIR)/coverage"

# Start test dashboard
.PHONY: dashboard
dashboard:
	docker-compose -f $(DOCKER_COMPOSE) up -d test-dashboard
	@echo "Test dashboard available at http://localhost:3000"

# Run continuous integration tests
.PHONY: ci
ci: clean setup test-coverage report

# Validate Docker Compose file
.PHONY: docker-validate
docker-validate:
	docker-compose -f $(DOCKER_COMPOSE) config

# Show test environment status
.PHONY: status
status:
	docker-compose -f $(DOCKER_COMPOSE) ps

# Remove all Docker volumes
.PHONY: docker-clean
docker-clean:
	docker-compose -f $(DOCKER_COMPOSE) down -v

# Install development tools
.PHONY: dev-tools
dev-tools:
	npm install -g jest cypress newman jmeter
	pip3 install pytest pytest-cov pytest-html locust bandit safety

# Run security scan
.PHONY: security-scan
security-scan:
	npm audit
	pip3 install safety
	safety check

# Run performance test with detailed output
.PHONY: perf-detailed
perf-detailed:
	mkdir -p $(RESULTS_DIR)/performance
	npm run test:performance > $(RESULTS_DIR)/performance/detailed.log 2>&1
	@echo "Performance test results saved to $(RESULTS_DIR)/performance/detailed.log"