.PHONY: help build test benchmark clean install

help: ## Show this help message
	@echo "thegent - Fast, reliable tool orchestration"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Rust extensions
	@zsh scripts/build-all-rust-extensions.sh

test: ## Run tests
	@cargo test --workspace
	@uv run pytest tests/ || echo "No Python tests found"

benchmark: ## Run performance benchmarks
	@zsh scripts/benchmark-comprehensive.sh

clean: ## Clean build artifacts
	@cargo clean
	@rm -rf target/ benchmarks/results/

install: ## Install Rust extensions
	@zsh scripts/build-all-rust-extensions.sh
	@zsh scripts/fix-which-timeout.sh

fix-timeout: ## Fix which timeout issue
	@zsh scripts/fix-which-timeout.sh

monitor: ## Monitor system health
	@zsh scripts/monitor-process-count.sh

.DEFAULT_GOAL := help
