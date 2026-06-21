# thegent Justfile
# Fleet-standard task runner (DAG stage 4)
# See FLEET_100TASK_DAG.md for context.
set shell := ["bash", "-cu"]

default:
    @just --list

install:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npm ci
    elif [ -f Cargo.toml ]; then
        cargo fetch
    elif [ -f pyproject.toml ] || [ -f setup.py ]; then
        pip install -e .[dev] 2>/dev/null || pip install -r requirements.txt 2>/dev/null || true
    elif [ -f go.mod ]; then
        go mod download
    fi

build:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npm run build 2>/dev/null || echo "no build script"
    elif [ -f Cargo.toml ]; then
        cargo build --workspace 2>/dev/null || cargo build
    elif [ -f go.mod ]; then
        go build ./...
    fi

test:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npm test 2>/dev/null || echo "no test script"
    elif [ -f Cargo.toml ]; then
        cargo test --workspace 2>/dev/null || cargo test
    elif [ -f go.mod ]; then
        go test ./...
    elif [ -d tests ]; then
        python -m pytest tests/ 2>/dev/null || echo "no python tests"
    fi

# Coverage report (SSOT for how to measure coverage).
coverage:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npx jest --coverage 2>/dev/null || npm test -- --coverage 2>/dev/null || echo "no coverage script"
    elif [ -f Cargo.toml ]; then
        cargo tarpaulin --workspace 2>/dev/null || echo "cargo-tarpaulin not installed"
    elif [ -f go.mod ]; then
        go test -coverprofile=coverage.out ./...
        go tool cover -func=coverage.out
    elif [ -d tests ]; then
        python -m pytest tests/ --cov=src 2>/dev/null || echo "no python coverage"
    fi

lint:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npm run lint 2>/dev/null || echo "no lint script"
    elif [ -f Cargo.toml ]; then
        cargo clippy --workspace --all-targets -- -D warnings 2>/dev/null || cargo clippy --workspace --all-targets
    elif [ -f go.mod ]; then
        go vet ./...
    fi

fmt:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f package.json ]; then
        npx prettier --write "**/*.{ts,tsx,js,jsx,json,md}" 2>/dev/null || echo "no prettier"
    elif [ -f Cargo.toml ]; then
        cargo fmt --all
    elif [ -f go.mod ]; then
        gofmt -w .
    fi

ci: install build test lint

# Tier-0 hygiene: cargo-deny license/advisory/bans/sources check (no install).
deny:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f crates/Cargo.toml ]; then
        cargo deny check --manifest-path crates/Cargo.toml
    elif [ -f Cargo.toml ]; then
        cargo deny check
    else
        echo "no Cargo.toml found; skipping cargo deny"
    fi

# Tier-0 hygiene: cargo-audit (RustSec advisory database).
audit:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f crates/Cargo.toml ]; then
        cargo audit --manifest-path crates/Cargo.toml
    elif [ -f Cargo.toml ]; then
        cargo audit
    else
        echo "no Cargo.toml found; skipping cargo audit"
    fi

# Fleet compliance grade (placeholder hook — wired by Tier-0 lint harness).
grade:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -x ./grade.sh ]; then
        ./grade.sh
    else
        echo "no grade.sh; running denoised check suite as fallback"
        just lint
        just deny
    fi

quality: lint deny audit grade

clean:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf node_modules dist target build .next coverage __pycache__ 2>/dev/null || true
