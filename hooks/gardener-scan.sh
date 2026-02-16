#!/usr/bin/env bash
# gardener-scan.sh — Hunger state detection
# Scans for conditions that need attention (like "hunger" in games)
# Based on research: vibecoding automation + DDD bounded contexts

set -euo pipefail

# Hunger detection functions

# Check test coverage
scan_test_coverage() {
    local coverage_threshold=80
    if command -v pytest &>/dev/null; then
        local coverage
        coverage=$(pytest --cov=fail --cov-report=term 2>/dev/null | grep -oP '\d+%' | head -1 || echo "0")
        coverage=${coverage%\%}
        if [[ "$coverage" -lt "$coverage_threshold" ]]; then
            echo "hunger: test_coverage current=$coverage threshold=$coverage_threshold priority=critical"
            return 0
        fi
    fi
    return 1
}

# Check lint violations
scan_lint_violations() {
    if command -v ruff &>/dev/null; then
        local violations
        violations=$(ruff check . 2>/dev/null | grep -c "error" || echo "0")
        if [[ "$violations" -gt 0 ]]; then
            echo "hunger: lint_violations current=$violations threshold=0 priority=critical"
            return 0
        fi
    fi
    return 1
}

# Check doc organization
scan_doc_disorganization() {
    local required_dirs=("docs/guides" "docs/reference" "docs/reports")
    local missing=0

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "${PROJECT_DIR:-.}/$dir" ]]; then
            missing=$((missing + 1))
        fi
    done

    if [[ "$missing" -gt 0 ]]; then
        echo "hunger: doc_disorganization current=$missing threshold=0 priority=high"
        return 0
    fi
    return 1
}

# Check fragmented research (research in wrong location)
scan_fragmented_research() {
    local specs_dir="${PROJECT_DIR:-.}/specs"
    [[ -d "$specs_dir" ]] || return 1

    # Check for research files outside the unified stream
    local fragmented
    fragmented=$(find "${PROJECT_DIR:-.}/docs" -name "*research*" -type f 2>/dev/null | wc -l || echo "0")

    if [[ "$fragmented" -gt 0 ]]; then
        echo "hunger: fragmented_research current=$fragmented threshold=0 priority=high"
        return 0
    fi
    return 1
}

# Check missing specs
scan_missing_specs() {
    local approved_dir="${PROJECT_DIR:-.}/specs/approved"
    [[ -d "$approved_dir" ]] || return 1

    # Check for features without SPEC.md
    local features
    features=$(find "$approved_dir" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l || echo "0")
    local has_specs
    has_specs=$(find "$approved_dir" -name "SPEC.md" 2>/dev/null | wc -l || echo "0")

    if [[ "$features" -gt 0 && "$has_specs" -eq 0 ]]; then
        echo "hunger: missing_specs current=$has_specs threshold=$features priority=medium"
        return 0
    fi
    return 1
}

# Check technical debt (complexity)
scan_technical_debt() {
    local threshold=10
    if command -v radon &>/dev/null; then
        local complexity
        complexity=$(radon cc . -a 2>/dev/null | grep -oP 'Average:\s*\K\d+' || echo "0")
        if [[ "$complexity" -gt "$threshold" ]]; then
            echo "hunger: technical_debt current=$complexity threshold=$threshold priority=medium"
            return 0
        fi
    fi
    return 1
}

# Check stale items in stream
scan_stale_items() {
    local stale_threshold=7
    local specs_dir="${PROJECT_DIR:-.}/specs"
    [[ -d "$specs_dir" ]] || return 1

    # Find items not modified in N days
    local stale_count
    stale_count=$(find "$specs_dir" -type f -mtime +${stale_threshold} 2>/dev/null | wc -l || echo "0")

    if [[ "$stale_count" -gt 0 ]]; then
        echo "hunger: stale_items current=$stale_count threshold_days=$stale_threshold priority=low"
        return 0
    fi
    return 1
}

# Check circuit breaker status
scan_agent_failure() {
    local circuit_breaker_file="${PROJECT_DIR:-.}/.thegent/sessions/circuit_breakers.jsonl"
    [[ -f "$circuit_breaker_file" ]] || return 1

    local open_count
    open_count=$(grep -c '"status": "OPEN"' "$circuit_breaker_file" 2>/dev/null || echo "0")

    if [[ "$open_count" -gt 0 ]]; then
        echo "hunger: agent_failure current=$open_count threshold=0 priority=critical"
        return 0
    fi
    return 1
}

# Main scan function
gardener_scan() {
    local detected_hungers=()

    echo "Scanning hunger states..."

    # Run all scans
    scan_test_coverage && detected_hungers+=("test_coverage")
    scan_lint_violations && detected_hungers+=("lint_violations")
    scan_doc_disorganization && detected_hungers+=("doc_disorganization")
    scan_fragmented_research && detected_hungers+=("fragmented_research")
    scan_missing_specs && detected_hungers+=("missing_specs")
    scan_technical_debt && detected_hungers+=("technical_debt")
    scan_stale_items && detected_hungers+=("stale_items")
    scan_agent_failure && detected_hungers+=("agent_failure")

    # Export results
    if [[ ${#detected_hungers[@]} -gt 0 ]]; then
        echo "Detected hunger states: ${detected_hungers[*]}"
        export GARDENER_DETECTED_HUNGERS="${detected_hungers[*]}"
    else
        echo "No hunger states detected"
        export GARDENER_DETECTED_HUNGERS=""
    fi

    return 0
}

# Run scan if sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    gardener_scan
fi
