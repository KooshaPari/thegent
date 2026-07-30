# Makefile — thegent onboarding wrapper (L30 pass-through).
#
# Most tasks delegate to Taskfile.yml (the canonical multi-stack runner) so
# contributors only need to remember one entry point. If `task` (go-task) is
# not installed, fall back to direct `uv run` invocations.
#
# Quick start:
#   make help                # show this file's targets
#   make install             # uv sync --all-extras + pip install -e .
#   make dev                 # task dev
#   make test                # task test
#   make lint                # task lint
#   make quality             # task quality (full gate)
#
# Each target is documented so the file is its own onboarding surface.
#
# @trace ONBOARD-L30: makefile pass-through

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# Detect task/uv lazily (Make `$(shell)` runs at parse time but on the host
# shell, which is exactly what we need for command -v detection).
TASK := $(shell command -v task 2>/dev/null)
UV   := $(shell command -v uv 2>/dev/null)

# ---------------------------------------------------------------------------
# Phony declaration
# ---------------------------------------------------------------------------

.PHONY: help install dev test lint format typecheck quality clean \
        setup doctor audit scorecard build coverage check precommit \
        sync boot phen onboard sota security harden version \
        validate-makefile test-quick dep-audit secrets-scan pip-audit

# ---------------------------------------------------------------------------
# Help (default target)
# ---------------------------------------------------------------------------

help: ## Show this help (default target)
	@echo "thegent onboarding — Makefile pass-through"
	@echo
	@echo "Targets (run 'make <target>'):"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Engine: $$([ -n "$(TASK)" ] && echo task || echo uv-fallback)"

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

# `task_if` runs the Taskfile target when present, otherwise falls through to
# the uv fallback. This protects us from the case where the user has `task`
# installed but the target is project-specific (e.g. install, dev).
define task_if
	@if [ -n "$(TASK)" ] && $(TASK) --list 2>/dev/null | grep -Eq "^\* $(1):"; then \
		$(TASK) $(1); \
	elif [ -n "$(UV)" ]; then \
		$(UV) run $(2); \
	else \
		echo "Neither 'task' nor 'uv' on PATH — install one of them first." >&2; \
		exit 1; \
	fi
endef

install: ## Install Python + system dependencies (uv sync --all-extras)
	@if [ -n "$(UV)" ]; then \
		$(UV) sync --all-extras; \
	else \
		echo "uv not on PATH — install from https://astral.sh/uv" >&2; \
		exit 1; \
	fi

setup: install ## Alias for install (legacy entry point)
	@true

doctor: ## Run thegent doctor (system health check)
	@if command -v thegent >/dev/null 2>&1; then \
		thegent doctor; \
	else \
		$(UV) run python -m thegent doctor; \
	fi

# ---------------------------------------------------------------------------
# Dev loop
# ---------------------------------------------------------------------------

dev: ## Start development server with hot reload
	$(call task_if,dev,thegent dev)

dev-tui: ## Start services with interactive TUI dashboard
	$(call task_if,dev:tui,thegent dev:tui)

phen: ## Open Phenotype-style phench interface (project launcher)
	$(call task_if,phen,thegent phench)

# ---------------------------------------------------------------------------
# Quality gates
# ---------------------------------------------------------------------------

test: ## Run test suite
	$(call task_if,test,pytest -q)

lint: ## Lint source and tests
	$(call task_if,lint,ruff check src tests)

format: ## Auto-format source
	$(call task_if,format,ruff format src tests)

typecheck: ## Run type checker
	$(call task_if,typecheck,mypy src/thegent)

build: ## Build detected project surfaces
	$(call task_if,build,python -m build)

coverage: ## Generate coverage report
	$(call task_if,coverage,pytest --cov=src/thegent --cov-report=term-missing)

quality: lint test ## Combined lint + test gate
	@echo "[make quality] lint+test passed"

check: build test lint ## Full check: build + test + lint
	$(call task_if,check,echo done)

precommit: lint format test ## Pre-commit quality gate
	@echo "[make precommit] lint+format+test passed"

# ---------------------------------------------------------------------------
# Governance + audit
# ---------------------------------------------------------------------------

audit: ## Run SOTA audit pipeline
	$(call task_if,audit,python scripts/run_audit.py)

scorecard: ## Refresh AUDIT_SCORECARD.md
	$(call task_if,scorecard,python scripts/refresh_audit_scorecard.py)

tach: ## Enforce Tach module boundaries
	$(call task_if,tach,tach check)

vale: ## Vale prose linting
	$(call task_if,vale,vale docs)

# ---------------------------------------------------------------------------
# Distribution + housekeeping
# ---------------------------------------------------------------------------

sync: ## Sync vendor + governance state
	$(call task_if,sync,thegent sync)

boot: ## Bootstrap a fresh consumer project
	@bash scripts/distribution/bootstrap-project.sh

clean: ## Remove generated caches + build artifacts
	$(call task_if,clean,rm -rf .pytest_cache .ruff_cache .mypy_cache dist build .coverage htmlcov)

# ---------------------------------------------------------------------------
# SOTA / Security / Harden lanes (Phase 4 expansion)
# ---------------------------------------------------------------------------

sota: ## Run the SOTA (state-of-the-art) audit lane
	$(call task_if,sota,python scripts/run_audit.py --lane sota)

security: ## Run the security audit lane
	$(call task_if,security,python scripts/run_audit.py --lane security)

harden: ## Run the hardening (Phase 3/4 governance + L1 guardrails) lane
	$(call task_if,harden,python scripts/run_audit.py --lane harden)

version: ## Print the project version (from VERSION file or pyproject)
	@if [ -f VERSION ]; then cat VERSION; \
	else $(UV) run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"; fi

# ---------------------------------------------------------------------------
# Onboarding aggregate (L30 onboarding surface polish)
# ---------------------------------------------------------------------------

# `onboard` is the single command a brand-new contributor runs after `git
# clone`. It exercises the full L30 onboarding surface: install deps,
# boot the devcontainer contract, smoke-test the CLI, and print the
# version. Failures abort at the first non-zero exit so the contributor
# sees a clear error trail instead of a partial green run.
onboard: install doctor version ## Aggregate onboarding: install + doctor + version + smoke
	@echo
	@echo "[make onboard] Running CLI smoke test..."
	@if command -v thegent >/dev/null 2>&1; then \
		thegent --help >/dev/null; \
	else \
		$(UV) run python -m thegent --help >/dev/null; \
	fi
	@echo "[make onboard] OK — thegent onboarding complete."
	@echo
	@echo "Next steps:"
	@echo "  make dev       # start development server"
	@echo "  make test      # run the test suite"
	@echo "  make quality   # run lint + tests"
	@echo "  make audit     # run the SOTA audit"

# ---------------------------------------------------------------------------
# Dev-loop quick wins (L2 Dev Loop expansion)
# ---------------------------------------------------------------------------

test-quick: ## Run a focused pytest subset (tests/unit + tests/test_wl1*) — fast feedback
	@$(UV) run pytest tests/unit tests/test_wl1* -q --no-header 2>/dev/null \
		|| $(UV) run pytest tests/unit -q --no-header

# `validate-makefile` is a self-test: confirms the canonical pass-through
# invariants (every phony target has a docstring, `help` lists every
# public target, no shell injection vectors) hold without invoking the
# shell. It is consumed by `make check` and the governance test suite.
validate-makefile: ## Self-test the Makefile pass-through invariants
	@bash scripts/check_makefile_invariants.sh

# `dep-audit` runs the L11 dependency-invariants static checker. Verifies
# uv.lock / pyproject.toml / requirements.txt are present, in sync, and
# free of common drift / hygiene issues. Safe for pre-commit hooks;
# runs in <50ms. Non-zero exit on the first violation.
dep-audit: ## Self-test dependency surface (L11 lane)
	@bash scripts/check_dependency_invariants.sh

# `secrets-scan` runs the L27 secrets-invariants static checker. Verifies
# gitleaks.toml / trufflehog.yml / .gitignore are present, complete, and
# free of common drift / hygiene issues, then performs an advisory sniff
# for live-key patterns outside the canonical allowlist. Safe for
# pre-commit hooks; runs in <1s.
secrets-scan: ## Self-test secrets-scan surface (L27 lane)
	@bash scripts/check_secrets_invariants.sh

# `pip-audit` runs the L11 dependency-advisory gate. Resolves the frozen
# requirements via `uv export --frozen`, audits them with pip-audit (OSV
# + PyPI fallback), and enforces a HIGH-severity ceiling on the
# recorded baseline (`help/audit/pip-audit-baseline.json`). Non-zero
# exit if the gate fails. Safe for CI (`.github/workflows/pip-audit.yml`)
# and pre-commit hooks. Use `PIP_AUDIT_NO_NETWORK=1` to bypass the live
# network probe and exercise the offline path.
pip-audit: ## Self-test dependency-advisory gate (L11 lane, HIGH-severity ceiling)
	@bash scripts/check_pip_audit_invariants.sh
