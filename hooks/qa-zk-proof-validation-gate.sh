#!/usr/bin/env bash
# qa-zk-proof-validation-gate.sh
# @trace FR-EXT-003
# Real implementation for WBS-F3 ZK proof validation gate.
# Runs circom/snarkjs when available; gracefully skips otherwise.
# Install: cp scripts/qa-zk-proof-validation-gate.sh ~/.claude/hooks/ && chmod +x ~/.claude/hooks/qa-zk-proof-validation-gate.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -----------------------------------------------------------------------------
# Tool availability checks
# -----------------------------------------------------------------------------
check_circom_available() {
    if command -v circom &>/dev/null; then
        return 0
    fi
    return 1
}

check_snarkjs_available() {
    if command -v snarkjs &>/dev/null; then
        return 0
    fi
    return 1
}

# -----------------------------------------------------------------------------
# Check if ZK is required for project
# -----------------------------------------------------------------------------
is_zk_required() {
    local project_dir="$1"
    local qfile="$project_dir/.claude/quality.json"

    if [[ ! -f "$qfile" ]]; then
        return 1
    fi

    local zk_required
    zk_required=$(jq -r '.governance.privacy_preserving.zk_required // false' "$qfile" 2>/dev/null || echo "false")
    [[ "$zk_required" == "true" ]]
}

# -----------------------------------------------------------------------------
# Find ZK artifacts in project
# -----------------------------------------------------------------------------
find_circom_files() {
    local project_dir="$1"
    find "$project_dir" -maxdepth 4 -name "*.circom" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true
}

find_zkey_files() {
    local project_dir="$1"
    find "$project_dir" -maxdepth 4 -name "*.zkey" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true
}

find_verification_keys() {
    local project_dir="$1"
    find "$project_dir" -maxdepth 4 -name "verification_key.json" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true
}

find_proof_files() {
    local project_dir="$1"
    find "$project_dir" -maxdepth 4 -name "proof.json" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true
}

has_zk_artifacts() {
    local project_dir="$1"
    [[ -n "$(find_circom_files "$project_dir")" ]] && return 0
    [[ -n "$(find_zkey_files "$project_dir")" ]] && return 0
    [[ -n "$(find_verification_keys "$project_dir")" ]] && return 0
    return 1
}

# -----------------------------------------------------------------------------
# Circom compilation
# -----------------------------------------------------------------------------
run_circom_compile() {
    local circom_file="$1"
    local output_dir="$2"
    local circom_dir
    circom_dir="$(dirname "$circom_file")"
    local circom_name
    circom_name="$(basename "$circom_file" .circom)"

    mkdir -p "$output_dir"

    pushd "$circom_dir" >/dev/null || return 1
    echo "  Running: circom $(basename "$circom_file") --r1cs --wasm --sym -o $output_dir"
    if circom "$(basename "$circom_file")" --r1cs --wasm --sym -o "$output_dir" 2>&1; then
        echo "  circom compile: PASS"
        popd >/dev/null || return 1
        return 0
    else
        echo "  circom compile: FAIL" >&2
        popd >/dev/null || return 1
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Snarkjs groth16 proof verification
# -----------------------------------------------------------------------------
run_snarkjs_verify() {
    local vkey_file="$1"
    local public_inputs="$2"
    local proof_file="$3"

    if [[ ! -f "$vkey_file" ]]; then
        echo "  SKIP: verification_key.json not found"
        return 0
    fi

    if [[ ! -f "$proof_file" ]]; then
        echo "  SKIP: proof.json not found"
        return 0
    fi

    if [[ ! -f "$public_inputs" ]]; then
        echo "  SKIP: public.json not found"
        return 0
    fi

    echo "  Running: snarkjs groth16 verify $vkey_file $public_inputs $proof_file"
    if snarkjs groth16 verify "$vkey_file" "$public_inputs" "$proof_file" 2>&1; then
        echo "  snarkjs verify: PASS"
        return 0
    else
        echo "  snarkjs verify: FAIL" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Generate ZK proof (for testing/development)
# -----------------------------------------------------------------------------
run_snarkjs_prove() {
    local zkey_file="$1"
    local witness_file="$2"
    local output_dir="$3"

    if [[ ! -f "$zkey_file" ]]; then
        echo "  SKIP: zkey file not found"
        return 0
    fi

    if [[ ! -f "$witness_file" ]]; then
        echo "  SKIP: witness file not found"
        return 0
    fi

    mkdir -p "$output_dir"

    echo "  Running: snarkjs groth16 prove $zkey_file $witness_file $output_dir/proof.json $output_dir/public.json"
    if snarkjs groth16 prove "$zkey_file" "$witness_file" "$output_dir/proof.json" "$output_dir/public.json" 2>&1; then
        echo "  snarkjs prove: PASS"
        return 0
    else
        echo "  snarkjs prove: FAIL" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Validate privacy-proof.json artifact
# -----------------------------------------------------------------------------
validate_privacy_proof_artifact() {
    local project_dir="$1"
    local proof_file="$project_dir/.claude/verification/privacy-proof.json"

    if [[ ! -f "$proof_file" ]]; then
        return 1
    fi

    # Check for proof_artifact or proof_ref or zk_proof
    if jq -e '.proof_artifact // .proof_ref // .zk_proof' "$proof_file" >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

# -----------------------------------------------------------------------------
# Main entry points
# -----------------------------------------------------------------------------
run_zk_validation() {
    local project_dir="$1"
    local verify_dir="$project_dir/.claude/verification"
    local report="$verify_dir/zk-proof-validation-gate.json"
    local privacy_proof="$verify_dir/privacy-proof.json"
    local now
    now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    mkdir -p "$verify_dir"

    # Check if ZK is required
    if ! is_zk_required "$project_dir"; then
        jq -n --arg ts "$now" '{
            generated_at: $ts,
            zk_required: false,
            status: "not_applicable",
            checks: [],
            pass: true,
            error_count: 0,
            warn_count: 0
        }' > "$report"
        echo "ZK PROOF VALIDATION: not applicable (zk_required=false)"
        return 0
    fi

    # ZK is required - check for tools
    if ! check_circom_available && ! check_snarkjs_available; then
        jq -n --arg ts "$now" '{
            generated_at: $ts,
            zk_required: true,
            status: "skip_no_tools",
            checks: [],
            pass: true,
            error_count: 0,
            warn_count: 0,
            warn: "ZK required but circom/snarkjs not installed"
        }' > "$report"
        echo "ZK PROOF VALIDATION: skip (tools not installed)"
        return 0
    fi

    echo "=== ZK PROOF VALIDATION GATE ==="
    echo "Project: $project_dir"
    echo ""

    local checks=()
    local errors=0
    local warns=0
    local overall_pass=true

    # Validate privacy-proof.json artifact
    if ! validate_privacy_proof_artifact "$project_dir"; then
        if [[ ! -f "$privacy_proof" ]]; then
            jq -n --arg ts "$now" '{
                generated_at: $ts,
                zk_required: true,
                status: "fail",
                checks: [],
                pass: false,
                error_count: 1,
                warn_count: 0,
                error: "privacy-proof.json missing"
            }' > "$report"
            echo "ZK-PROOF-VALIDATION FAIL: privacy-proof.json missing" >&2
            return 2
        fi
        checks+=("{\"name\":\"privacy_proof_artifact\",\"status\":\"warn\",\"message\":\"proof_artifact not populated\"}")
        ((warns++)) || true
    else
        checks+=("{\"name\":\"privacy_proof_artifact\",\"status\":\"pass\"}")
    fi

    # Check for ZK circuit artifacts
    local circom_files
    circom_files=$(find_circom_files "$project_dir")
    local vkey_files
    vkey_files=$(find_verification_keys "$project_dir")
    local proof_files
    proof_files=$(find_proof_files "$project_dir")

    # Compile circom circuits if present
    if [[ -n "$circom_files" ]] && check_circom_available; then
        while IFS= read -r circom_file; do
            [[ -z "$circom_file" ]] && continue
            echo "Compiling circuit: $circom_file"
            local output_dir="$verify_dir/zk-circuits"
            if ! run_circom_compile "$circom_file" "$output_dir"; then
                checks+=("{\"name\":\"circom_compile_$(basename "$circom_file")\",\"status\":\"fail\"}")
                ((errors++)) || true
                overall_pass=false
            else
                checks+=("{\"name\":\"circom_compile_$(basename "$circom_file")\",\"status\":\"pass\"}")
            fi
        done <<< "$circom_files"
    fi

    # Verify proofs if verification keys and proofs exist
    if [[ -n "$vkey_files" ]] && check_snarkjs_available; then
        while IFS= read -r vkey_file; do
            [[ -z "$vkey_file" ]] && continue
            local vkey_dir
            vkey_dir="$(dirname "$vkey_file")"

            # Look for matching proof and public inputs
            local proof_file="$vkey_dir/proof.json"
            local public_file="$vkey_dir/public.json"

            if [[ -f "$proof_file" && -f "$public_file" ]]; then
                echo "Verifying proof: $proof_file"
                if ! run_snarkjs_verify "$vkey_file" "$public_file" "$proof_file"; then
                    checks+=("{\"name\":\"snarkjs_verify_$(dirname "$vkey_file" | xargs basename)\",\"status\":\"fail\"}")
                    ((errors++)) || true
                    overall_pass=false
                else
                    checks+=("{\"name\":\"snarkjs_verify_$(dirname "$vkey_file" | xargs basename)\",\"status\":\"pass\"}")
                fi
            else
                echo "  SKIP: No matching proof/public.json for $vkey_file"
                checks+=("{\"name\":\"snarkjs_verify_$(dirname "$vkey_file" | xargs basename)\",\"status\":\"skip\",\"message\":\"missing proof or public inputs\"}")
            fi
        done <<< "$vkey_files"
    fi

    # Build JSON report
    local checks_json
    checks_json=$(printf '%s\n' "${checks[@]}" | jq -s '.' 2>/dev/null || echo '[]')
    local pass_json="true"
    [[ "$overall_pass" == "false" ]] && pass_json="false"

    jq -n --arg ts "$now" --argjson checks "$checks_json" --argjson pass "$pass_json" --argjson errors "$errors" --argjson warns "$warns" '{
        generated_at: $ts,
        zk_required: true,
        status: "evaluated",
        checks: $checks,
        pass: $pass,
        error_count: $errors,
        warn_count: $warns
    }' > "$report"

    echo ""
    if [[ "$overall_pass" == "true" ]]; then
        echo "ZK PROOF VALIDATION: PASS"
        return 0
    else
        echo "ZK PROOF VALIDATION: FAIL ($errors errors, $warns warnings)" >&2
        return 1
    fi
}

# Hook mode (reads JSON from stdin)
run_hook_mode() {
    local input
    input="$(cat)"
    local cwd
    cwd="$(jq -r '.cwd // empty' <<< "$input")"
    local project_dir="${cwd:-$(pwd)}"

    run_zk_validation "$project_dir"
}

# CLI mode with options
run_cli_mode() {
    local project_dir="."
    local mode="check"
    local proof_file=""
    local public_inputs=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check)
                mode="check"
                project_dir="${2:-.}"
                shift 2 || shift
                ;;
            --verify)
                mode="verify"
                proof_file="$2"
                shift 2
                ;;
            --public-inputs)
                public_inputs="$2"
                shift 2
                ;;
            *)
                project_dir="$1"
                shift
                ;;
        esac
    done

    if [[ "$mode" == "verify" ]]; then
        # Direct verification mode
        if [[ -z "$proof_file" ]]; then
            echo "Error: --verify requires proof file path" >&2
            exit 2
        fi

        if ! check_snarkjs_available; then
            echo "SKIP: snarkjs not installed"
            exit 0
        fi

        local proof_dir
        proof_dir="$(dirname "$proof_file")"
        local vkey_file="$proof_dir/verification_key.json"
        local public_file="${public_inputs:-$proof_dir/public.json}"

        if [[ ! -f "$vkey_file" ]]; then
            echo "Error: verification_key.json not found at $vkey_file" >&2
            exit 2
        fi

        if [[ ! -f "$public_file" ]]; then
            echo "Error: public inputs not found at $public_file" >&2
            exit 2
        fi

        run_snarkjs_verify "$vkey_file" "$public_file" "$proof_file"
        exit $?
    fi

    # Default check mode
    run_zk_validation "$(cd "$project_dir" && pwd)"
}

# Main
if [[ -t 0 ]]; then
    # Interactive/CLI mode
    run_cli_mode "$@"
else
    # Hook mode (piped input)
    run_hook_mode
fi
