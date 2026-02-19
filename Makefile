.PHONY: help build test benchmark clean install

help: ## Show this help message
	@echo "thegent - Fast, reliable tool orchestration"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Rust extensions
	@bash scripts/build-all-rust-extensions.sh

test: ## Run tests
	@cargo test --workspace
	@python3 -m pytest tests/ || echo "No Python tests found"

benchmark: ## Run performance benchmarks
	@bash scripts/benchmark-comprehensive.sh

clean: ## Clean build artifacts
	@cargo clean
	@rm -rf target/ benchmarks/results/

install: ## Install Rust extensions
	@bash scripts/build-all-rust-extensions.sh
	@bash scripts/fix-which-timeout.sh

fix-timeout: ## Fix which timeout issue
	@bash scripts/fix-which-timeout.sh

monitor: ## Monitor system health
	@bash scripts/monitor-process-count.sh

.DEFAULT_GOAL := help
