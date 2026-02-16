#!/usr/bin/env bash
# security-pipeline.sh — Stop hook
# Multi-layer security scanning pipeline. Advisory only (exit 0 always).
# SOLE OWNER of: gitleaks, bandit, tfsec (removed from quality-gate)
# Layers: Secrets, SAST, Dependencies, Infrastructure, Supply Chain & SBOM.
# Budget: <60s total. All 5 layers run in parallel; within-layer tools also parallel.
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
# Cache git HEAD once to avoid repeated git calls throughout hook
readonly _GIT_HEAD_SHA="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="$_GIT_HEAD_SHA"
_CACHE_FILE="${_CACHE_DIR}/security-pipeline-${_CACHE_KEY}.result"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < _CACHE_TTL )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

# --- Early: check if ANY security tool is available BEFORE common.sh ---
# Quick probe: check the most common tools first, exit early if ANY found
_any_tool=false
for _t in gitleaks semgrep bandit; do
  command -v "$_t" >/dev/null 2>&1 && { _any_tool=true; break; }
done
if [[ "$_any_tool" == "false" ]]; then
  # Check remaining tools
  for _t in gosec pip-audit govulncheck cargo-audit hadolint tfsec trivy syft osv-scanner opengrep; do
    command -v "$_t" >/dev/null 2>&1 && { _any_tool=true; break; }
  done
fi
if [[ "$_any_tool" == "false" ]]; then
  # No security tools installed — emit minimal report and exit fast (no common.sh needed)
  printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
  _PD="${PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  RESULTS_FILE="$HOME/.claude/.security-scan-results.json"
  echo ""
  echo "Security Pipeline Report"
  echo "========================"
  echo "Layer 1 - Secrets:        SKIP (tool unavailable)"
  echo "Layer 2 - SAST:           SKIP (tool unavailable)"
  echo "Layer 3 - Dependencies:   SKIP (tool unavailable)"
  echo "Layer 4 - Infrastructure: SKIP (tool unavailable)"
  echo "Layer 5 - Supply Chain:  SKIP (tool unavailable)"
  mkdir -p "$(dirname "$RESULTS_FILE")" 2>/dev/null || true
  printf '{"timestamp":"%s","project":"%s","layers":["secrets","sast","deps","infra","supply_chain"],"summary":{"layer1_secrets":{"status":"SKIP","count":0},"layer2_sast":{"status":"SKIP","count":0},"layer3_deps":{"status":"SKIP","count":0},"layer4_infra":{"status":"SKIP","count":0},"layer5_supply_chain":{"status":"SKIP","count":0},"total_findings":0},"findings":[]}\n' \
    "$now" "$_PD" > "$RESULTS_FILE"
  exit 0
fi

HOOK_NAME="SECURITY-PIPELINE"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Stderr message on unexpected failure (set -e)
trap 'echo "SECURITY-PIPELINE FAIL: unexpected error at line $LINENO" >&2' ERR

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

# --- P1 optimization: Skip if no security-relevant files changed ---
# Security scans are expensive - only run if source/config files changed
if ! any_source_changed; then
  echo "SECURITY-PIPELINE: skipped (no source files changed)"
  exit 0
fi

RESULTS_FILE="$HOME/.claude/.security-scan-results.json"

# ---------- Detect project types ----------
is_python=false; is_node=false; is_go=false; is_rust=false
[[ -f "$PROJECT_DIR/pyproject.toml" || -f "$PROJECT_DIR/setup.py" || -f "$PROJECT_DIR/requirements.txt" ]] && is_python=true
[[ -f "$PROJECT_DIR/package.json" ]] && is_node=true
[[ -f "$PROJECT_DIR/go.mod" ]] && is_go=true
[[ -f "$PROJECT_DIR/Cargo.toml" ]] && is_rust=true

# --- Cache check — skip if HEAD unchanged ---
# Use cached git HEAD value from above (readonly _GIT_HEAD_SHA) to avoid second git call
_sec_cache_key=$(printf '%s\0%s' "$HOOK_NAME" "$_GIT_HEAD_SHA" | shasum -a 256 | cut -d' ' -f1)
_sec_ttl="${HOOK_CACHE_TTL:-600}"
if hook_cache_check "$_sec_cache_key" "$_sec_ttl"; then
    _sec_output=$(hook_cache_read "$_sec_cache_key")
    _cached_rc=$?
    # Write ultra-fast cache
    mkdir -p "$_CACHE_DIR" 2>/dev/null || true
    echo "$_sec_output" > "$_CACHE_FILE" 2>/dev/null || true
    echo "$_sec_output"
    if [[ "$_cached_rc" -ne 0 ]]; then
      echo "SECURITY-PIPELINE FAIL: cached result was non-zero ($_cached_rc)" >&2
    fi
    exit "$_cached_rc"
fi

# ---------- Collect changed files ----------
declare -a CHANGED_FILES=()
mapfile -t CHANGED_FILES < <(get_changed_files | grep -v '^$')

# Fallback to hook_shared_changed_files if no session log
if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  declare -a _fallback_files=()
  mapfile -t _fallback_files < <(hook_shared_changed_files 2>/dev/null | grep -v '^$')
  for fpath in "${_fallback_files[@]}"; do
    [[ -f "$PROJECT_DIR/$fpath" ]] && CHANGED_FILES+=("$PROJECT_DIR/$fpath")
  done
fi

has_changed_files=true
[[ ${#CHANGED_FILES[@]} -eq 0 ]] && has_changed_files=false

# ---------- Parallel infrastructure ----------
# Each layer writes to $tmpdir/layerN.{findings,count,status}
# Findings: one line per finding. Count: single integer. Status: PASS|WARN|SKIP.
tmpdir=$(mktemp -d "/tmp/secpipe-$$.XXXXXX")
trap 'rm -rf "$tmpdir"' EXIT

# Export variables that subshells need
export is_python is_node is_go is_rust has_changed_files PROJECT_DIR tmpdir

# Write the CHANGED_FILES array to a file so subshells can read it
printf '%s\n' "${CHANGED_FILES[@]}" > "$tmpdir/changed_files.list" 2>/dev/null || true

# Helper: read CHANGED_FILES from the temp file (for use inside layer functions)
_load_changed_files() {
  CHANGED_FILES=()
  if [[ -f "$tmpdir/changed_files.list" ]]; then
    mapfile -t CHANGED_FILES < <(grep -v '^$' "$tmpdir/changed_files.list")
  fi
  has_changed_files=true
  [[ ${#CHANGED_FILES[@]} -eq 0 ]] && has_changed_files=false
}

# ========== LAYER 1 -- Secret Detection ==========
layer1_secrets() {
  _load_changed_files
  local count=0
  local ran=false
  local findings_file="$tmpdir/layer1.findings"
  : > "$findings_file"

  if _has_tool gitleaks; then
    ran=true
    gitleaks_out=$(run_with_timeout 15 gitleaks detect --no-git --source "$PROJECT_DIR" --no-banner 2>/dev/null) || { echo "SECURITY-PIPELINE: gitleaks failed ($?)" >&2; true; }
    if [[ -n "$gitleaks_out" ]]; then
      c=$(echo "$gitleaks_out" | grep -c "Finding:" 2>/dev/null || echo "0")
      count=$((count + c))
      echo "$gitleaks_out" | grep -E "^(Finding|File|Line)" 2>/dev/null | head -20 | sed 's/^/[HIGH] secrets: /' >> "$findings_file"
    fi
  fi

  # Fallback: grep-based secret detection on changed files
  if [[ "$has_changed_files" == true ]]; then
    ran=true
    local secret_patterns=(
      '(?i)(api[_-]?key|apikey)\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'
      '(?i)(secret|password|passwd|pwd)\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'
      '(?i)(token|bearer)\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'
      '(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*['"'"'"][^'"'"'"]{16,}'
      '-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----'
      'ghp_[a-zA-Z0-9]{36}'
      'sk-[a-zA-Z0-9]{20,}'
    )
    for fpath in "${CHANGED_FILES[@]}"; do
      [[ "$fpath" =~ \.(lock|lockb|png|jpg|gif|ico|woff|ttf|eot|svg|pdf)$ ]] && continue
      [[ "$fpath" =~ (fixture|mock|fake|stub|test_data|testdata) ]] && continue
      for pat in "${secret_patterns[@]}"; do
        matches=$(PAT="$pat" perl -ne 'print "$.: $_" if /$ENV{PAT}/i' "$fpath" 2>/dev/null | head -5) || true
        if [[ -n "$matches" ]]; then
          rel_path="${fpath#"$PROJECT_DIR"/}"
          echo "$matches" | sed 's/^\([0-9]*\):.*/[HIGH] secrets: Possible secret in '"$rel_path"':\1/' >> "$findings_file"
          count=$((count + $(echo "$matches" | wc -l)))
        fi
      done
    done

    # Hardcoded IP check (exclude localhost patterns)
    for fpath in "${CHANGED_FILES[@]}"; do
      [[ "$fpath" =~ \.(lock|lockb|png|jpg|gif|ico|woff|ttf|eot|svg|pdf|md)$ ]] && continue
      ip_matches=$(perl -ne 'print "$.: $_" if /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/ && !/127\.0\.0\.1|0\.0\.0\.0|localhost|255\.255\.\d+\.\d+|192\.168\.|10\.\d+\.|172\.(1[6-9]|2[0-9]|3[01])\./' "$fpath" 2>/dev/null | head -5) || true
      if [[ -n "$ip_matches" ]]; then
        rel_path="${fpath#"$PROJECT_DIR"/}"
        echo "$ip_matches" | sed 's/^\([0-9]*\):.*/[MEDIUM] secrets: Hardcoded IP in '"$rel_path"':\1/' >> "$findings_file"
        count=$((count + $(echo "$ip_matches" | wc -l)))
      fi
    done
  fi

  if [[ "$ran" == true ]]; then
    [[ $count -eq 0 ]] && echo "PASS" > "$tmpdir/layer1.status" || echo "WARN" > "$tmpdir/layer1.status"
  else
    echo "SKIP" > "$tmpdir/layer1.status"
  fi
  echo "$count" > "$tmpdir/layer1.count"
}

# ========== LAYER 2 -- SAST (semgrep, bandit, gosec in parallel) ==========
layer2_sast() {
  _load_changed_files
  local ran=false
  local subtmp="$tmpdir/layer2_sub"
  mkdir -p "$subtmp"

  # --- semgrep (background) ---
  if _has_tool semgrep && [[ "$has_changed_files" == true ]]; then
    ran=true
    (
      local count=0
      semgrep_out=$(run_with_timeout 20 semgrep --config=auto --quiet "${CHANGED_FILES[@]}" 2>/dev/null) || { echo "SECURITY-PIPELINE: semgrep failed ($?)" >&2; true; }
      if [[ -n "$semgrep_out" ]]; then
        count=$(echo "$semgrep_out" | grep -cE "^[[:space:]]*(error|warning)" 2>/dev/null || echo "0")
        echo "$semgrep_out" | head -20 | sed 's/^/[MEDIUM] sast: /' > "$subtmp/semgrep.findings"
      fi
      echo "$count" > "$subtmp/semgrep.count"
    ) &
  fi

  # --- bandit (background) ---
  if [[ "$is_python" == true ]] && _has_tool bandit; then
    ran=true
    (
      local count=0
      bandit_out=$(run_with_timeout 15 bandit -r "$PROJECT_DIR" -q 2>/dev/null) || { echo "SECURITY-PIPELINE: bandit failed ($?)" >&2; true; }
      if [[ -n "$bandit_out" ]]; then
        count=$(echo "$bandit_out" | grep -cE "^>>" 2>/dev/null || echo "0")
        echo "$bandit_out" | grep -E "^>>" | head -10 | sed 's/^/[MEDIUM] sast\/bandit: /' > "$subtmp/bandit.findings"
      fi
      echo "$count" > "$subtmp/bandit.count"
    ) &
  fi

  # --- gosec (background) ---
  if [[ "$is_go" == true ]] && _has_tool gosec; then
    ran=true
    (
      local count=0
      gosec_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 gosec ./... 2>/dev/null) || { echo "SECURITY-PIPELINE: gosec failed ($?)" >&2; true; }
      if [[ -n "$gosec_out" ]]; then
        count=$(echo "$gosec_out" | grep -cE "^\[" 2>/dev/null || echo "0")
        echo "$gosec_out" | grep -E "^\[" | head -10 | sed 's/^/[MEDIUM] sast\/gosec: /' > "$subtmp/gosec.findings"
      fi
      echo "$count" > "$subtmp/gosec.count"
    ) &
  fi

  wait

  # Collect results from sub-tools
  local total_count=0
  for f in "$subtmp"/*.count; do
    [[ -f "$f" ]] || continue
    c=$(cat "$f" 2>/dev/null || echo "0")
    total_count=$((total_count + c))
  done
  cat "$subtmp"/*.findings > "$tmpdir/layer2.findings" 2>/dev/null || : > "$tmpdir/layer2.findings"

  if [[ "$ran" == true ]]; then
    [[ $total_count -eq 0 ]] && echo "PASS" > "$tmpdir/layer2.status" || echo "WARN" > "$tmpdir/layer2.status"
  else
    echo "SKIP" > "$tmpdir/layer2.status"
  fi
  echo "$total_count" > "$tmpdir/layer2.count"
}

# ========== LAYER 3 -- Dependency Audit (all auditors in parallel) ==========
layer3_deps() {
  _load_changed_files
  local ran=false
  local subtmp="$tmpdir/layer3_sub"
  mkdir -p "$subtmp"

  # --- pip-audit (background) ---
  if [[ "$is_python" == true ]] && _has_tool pip-audit; then
    ran=true
    (
      local count=0
      audit_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 pip-audit 2>/dev/null) || { echo "SECURITY-PIPELINE: pip-audit failed ($?)" >&2; true; }
      if [[ -n "$audit_out" ]]; then
        count=$(echo "$audit_out" | grep -cE "^Name" 2>/dev/null || echo "0")
        [[ $count -gt 0 ]] && count=$((count - 1))
        echo "$audit_out" | grep -vE "^(Name|---)" | head -10 | sed 's/^/[HIGH] deps\/pip-audit: /' > "$subtmp/pip-audit.findings"
      fi
      echo "$count" > "$subtmp/pip-audit.count"
    ) &
  fi

  # --- bun audit / npm audit (background) ---
  if [[ "$is_node" == true ]]; then
    if [[ -f "$PROJECT_DIR/bun.lockb" || -f "$PROJECT_DIR/bun.lock" ]] && _has_tool bun; then
      ran=true
      (
        local count=0
        audit_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 bun audit 2>/dev/null) || { echo "SECURITY-PIPELINE: bun audit failed ($?)" >&2; true; }
        if echo "$audit_out" | grep -qiE "(high|critical)" 2>/dev/null; then
          count=$(echo "$audit_out" | grep -ciE "(high|critical)" 2>/dev/null || echo "0")
          echo "[HIGH] deps/bun: $count high/critical vulnerabilities" > "$subtmp/bun.findings"
        fi
        echo "$count" > "$subtmp/bun.count"
      ) &
    elif [[ -f "$PROJECT_DIR/package-lock.json" ]] && _has_tool npm; then
      ran=true
      (
        local count=0
        audit_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 npm audit --audit-level=high 2>/dev/null) || { echo "SECURITY-PIPELINE: npm audit failed ($?)" >&2; true; }
        if echo "$audit_out" | grep -qiE "(high|critical)" 2>/dev/null; then
          count=$(echo "$audit_out" | grep -ciE "(high|critical)" 2>/dev/null || echo "0")
          echo "[HIGH] deps/npm: $count high/critical vulnerabilities" > "$subtmp/npm.findings"
        fi
        echo "$count" > "$subtmp/npm.count"
      ) &
    fi
  fi

  # --- govulncheck (background) ---
  if [[ "$is_go" == true ]] && _has_tool govulncheck; then
    ran=true
    (
      local count=0
      vuln_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 govulncheck ./... 2>/dev/null) || { echo "SECURITY-PIPELINE: govulncheck failed ($?)" >&2; true; }
      if [[ -n "$vuln_out" ]] && echo "$vuln_out" | grep -qE "^Vulnerability" 2>/dev/null; then
        count=$(echo "$vuln_out" | grep -cE "^Vulnerability" 2>/dev/null || echo "0")
        echo "$vuln_out" | grep -E "^Vulnerability" | head -10 | sed 's/^/[HIGH] deps\/govulncheck: /' > "$subtmp/govulncheck.findings"
      fi
      echo "$count" > "$subtmp/govulncheck.count"
    ) &
  fi

  # --- cargo audit (background) ---
  if [[ "$is_rust" == true ]] && _has_tool cargo-audit; then
    ran=true
    (
      local count=0
      audit_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 cargo audit 2>/dev/null) || { echo "SECURITY-PIPELINE: cargo audit failed ($?)" >&2; true; }
      if echo "$audit_out" | grep -qE "^(error|warning)\[" 2>/dev/null; then
        count=$(echo "$audit_out" | grep -cE "^(error|warning)\[" 2>/dev/null || echo "0")
        echo "$audit_out" | grep -E "^(error|warning)\[" | head -10 | sed 's/^/[HIGH] deps\/cargo-audit: /' > "$subtmp/cargo-audit.findings"
      fi
      echo "$count" > "$subtmp/cargo-audit.count"
    ) &
  fi

  wait

  # Collect results from sub-tools
  local total_count=0
  for f in "$subtmp"/*.count; do
    [[ -f "$f" ]] || continue
    c=$(cat "$f" 2>/dev/null || echo "0")
    total_count=$((total_count + c))
  done
  cat "$subtmp"/*.findings > "$tmpdir/layer3.findings" 2>/dev/null || : > "$tmpdir/layer3.findings"

  if [[ "$ran" == true ]]; then
    [[ $total_count -eq 0 ]] && echo "PASS" > "$tmpdir/layer3.status" || echo "WARN" > "$tmpdir/layer3.status"
  else
    echo "SKIP" > "$tmpdir/layer3.status"
  fi
  echo "$total_count" > "$tmpdir/layer3.count"
}

# ========== LAYER 4 -- Infrastructure (hadolint, tfsec, trivy in parallel) ==========
layer4_infra() {
  _load_changed_files
  local ran=false
  local subtmp="$tmpdir/layer4_sub"
  mkdir -p "$subtmp"

  # --- hadolint: parallelize across Dockerfiles (background) ---
  if _has_tool hadolint; then
    local -a dockerfiles=()
    # Fast check: look for common Dockerfile locations before expensive find
    for _df_candidate in Dockerfile Dockerfile.dev Dockerfile.prod docker/Dockerfile; do
      [[ -f "$PROJECT_DIR/$_df_candidate" ]] && dockerfiles+=("$PROJECT_DIR/$_df_candidate")
    done
    # Only fall back to find if no common names matched
    if [[ ${#dockerfiles[@]} -eq 0 ]]; then
      mapfile -t dockerfiles < <(find "$PROJECT_DIR" -maxdepth 2 -name "Dockerfile*" -type f 2>/dev/null)
    fi
    if [[ ${#dockerfiles[@]} -gt 0 ]]; then
      ran=true
      local i=0
      for df in "${dockerfiles[@]}"; do
        (
          local count=0
          hadolint_out=$(run_with_timeout 10 hadolint "$df" 2>/dev/null) || { echo "SECURITY-PIPELINE: hadolint failed ($?)" >&2; true; }
          if [[ -n "$hadolint_out" ]]; then
            count=$(echo "$hadolint_out" | wc -l | tr -d ' ')
            echo "$hadolint_out" | head -10 | sed 's/^/[MEDIUM] infra\/hadolint: /' > "$subtmp/hadolint-$i.findings"
          fi
          echo "$count" > "$subtmp/hadolint-$i.count"
        ) &
        i=$((i + 1))
      done
    fi
  fi

  # --- tfsec (background) ---
  if _has_tool tfsec; then
    # Fast check: common tf locations before expensive find
    local tf_files=""
    for _tf_dir in . terraform infra infrastructure deploy; do
      if compgen -G "$PROJECT_DIR/$_tf_dir/*.tf" >/dev/null 2>&1; then
        tf_files="found"; break
      fi
    done
    # Only fall back to find if quick check found nothing
    if [[ -z "$tf_files" ]]; then
      tf_files=$(find "$PROJECT_DIR" -maxdepth 3 -name "*.tf" -type f 2>/dev/null | head -1)
    fi
    if [[ -n "$tf_files" ]]; then
      ran=true
      (
        local count=0
        tfsec_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 tfsec --no-color 2>/dev/null) || { echo "SECURITY-PIPELINE: tfsec failed ($?)" >&2; true; }
        if [[ -n "$tfsec_out" ]]; then
          count=$(echo "$tfsec_out" | grep -cE "^Result" 2>/dev/null || echo "0")
          echo "$tfsec_out" | grep -E "^Result" | head -10 | sed 's/^/[HIGH] infra\/tfsec: /' > "$subtmp/tfsec.findings"
        fi
        echo "$count" > "$subtmp/tfsec.count"
      ) &
    fi
  fi

  # --- trivy (background) ---
  if _has_tool trivy; then
    ran=true
    (
      local count=0
      trivy_out=$(cd "$PROJECT_DIR" && run_with_timeout 15 trivy config . --severity HIGH,CRITICAL 2>/dev/null) || { echo "SECURITY-PIPELINE: trivy failed ($?)" >&2; true; }
      if [[ -n "$trivy_out" ]] && echo "$trivy_out" | grep -qE "(HIGH|CRITICAL)" 2>/dev/null; then
        count=$(echo "$trivy_out" | grep -cE "(HIGH|CRITICAL)" 2>/dev/null || echo "0")
        echo "$trivy_out" | grep -E "(HIGH|CRITICAL)" | head -10 | sed 's/^/[HIGH] infra\/trivy: /' > "$subtmp/trivy.findings"
      fi
      echo "$count" > "$subtmp/trivy.count"
    ) &
  fi

  wait

  # Collect results from sub-tools
  local total_count=0
  for f in "$subtmp"/*.count; do
    [[ -f "$f" ]] || continue
    c=$(cat "$f" 2>/dev/null || echo "0")
    total_count=$((total_count + c))
  done
  cat "$subtmp"/*.findings > "$tmpdir/layer4.findings" 2>/dev/null || : > "$tmpdir/layer4.findings"

  if [[ "$ran" == true ]]; then
    [[ $total_count -eq 0 ]] && echo "PASS" > "$tmpdir/layer4.status" || echo "WARN" > "$tmpdir/layer4.status"
  else
    echo "SKIP" > "$tmpdir/layer4.status"
  fi
  echo "$total_count" > "$tmpdir/layer4.count"
}

# ========== LAYER 5 -- Supply Chain & SBOM (syft, osv-scanner, opengrep in parallel) ==========
layer5_supply_chain() {
  _load_changed_files
  local ran=false
  local subtmp="$tmpdir/layer5_sub"
  mkdir -p "$subtmp"

  # --- 5a. SBOM Generation (syft) (background) ---
  if _has_tool syft; then
    ran=true
    (
      sbom_tmp="/tmp/sbom-$$.json"
      syft_out=$(cd "$PROJECT_DIR" && run_with_timeout 30 syft . --output "cyclonedx-json=$sbom_tmp" 2>&1) || { echo "SECURITY-PIPELINE: syft failed ($?)" >&2; true; }
      if [[ -f "$sbom_tmp" ]]; then
        echo "$sbom_tmp" > "$subtmp/sbom_path"
        component_count=$($JQ_CMD '.components | length' "$sbom_tmp" 2>/dev/null || echo "unknown")
        echo "SBOM: Generated CycloneDX SBOM ($component_count components)" > "$subtmp/sbom.stdout"
      fi
    ) &
  fi

  # --- 5b. OSV-Scanner: parallelize across lockfiles (background per lockfile) ---
  if _has_tool osv-scanner; then
    declare -a lockfiles=()
    for lockfile in requirements.txt package-lock.json bun.lock go.sum Cargo.lock Gemfile.lock composer.lock; do
      [[ -f "$PROJECT_DIR/$lockfile" ]] && lockfiles+=("$PROJECT_DIR/$lockfile")
    done

    if [[ ${#lockfiles[@]} -gt 0 ]]; then
      ran=true
      local i=0
      for lockfile in "${lockfiles[@]}"; do
        (
          local count=0
          osv_out=$(run_with_timeout 30 osv-scanner scan --lockfile="$lockfile" --format json 2>/dev/null) || true
          if [[ -n "$osv_out" ]]; then
            vuln_count=$(echo "$osv_out" | $JQ_CMD '[.results[]?.packages[]?.vulnerabilities[]?] | length' 2>/dev/null || echo "0")
            if [[ "$vuln_count" -gt 0 ]] 2>/dev/null; then
              count=$vuln_count
              lockfile_name="${lockfile##*/}"
              declare -a osv_findings=()
              mapfile -t osv_findings < <(
                echo "$osv_out" | $JQ_CMD -c '.results[]?.packages[]?.vulnerabilities[]?' 2>/dev/null | head -20
              )
              {
                for vuln_line in "${osv_findings[@]}"; do
                  cve_id=$(echo "$vuln_line" | $JQ_CMD -r '.id // "unknown"' 2>/dev/null || echo "unknown")
                  pkg_name=$(echo "$vuln_line" | $JQ_CMD -r '.package.name // "unknown"' 2>/dev/null || echo "unknown")
                  pkg_ver=$(echo "$vuln_line" | $JQ_CMD -r '.package.version // "unknown"' 2>/dev/null || echo "unknown")
                  echo "[HIGH] dependency: $cve_id in $pkg_name@$pkg_ver ($lockfile_name)"
                done
              } > "$subtmp/osv-$i.findings"
            fi
          fi
          echo "$count" > "$subtmp/osv-$i.count"
        ) &
        i=$((i + 1))
      done
    fi
  fi

  # --- 5c. Opengrep (enhanced SAST) (background) ---
  if _has_tool opengrep && [[ "$has_changed_files" == true ]]; then
    ran=true
    (
      local count=0
      opengrep_out=$(run_with_timeout 20 opengrep --config auto --json "${CHANGED_FILES[@]}" 2>/dev/null) || true
      if [[ -n "$opengrep_out" ]]; then
        count=$(echo "$opengrep_out" | $JQ_CMD '.results | length' 2>/dev/null || echo "0")
        if [[ "$count" -gt 0 ]] 2>/dev/null; then
          declare -a og_findings=()
        mapfile -t og_findings < <(
          echo "$opengrep_out" | $JQ_CMD -c '.results[]?' 2>/dev/null | head -20
        )
        {
          for result_line in "${og_findings[@]}"; do
            check_id=$(echo "$result_line" | $JQ_CMD -r '.check_id // "unknown"' 2>/dev/null || echo "unknown")
            og_path=$(echo "$result_line" | $JQ_CMD -r '.path // "unknown"' 2>/dev/null || echo "unknown")
            og_line=$(echo "$result_line" | $JQ_CMD -r '.start.line // "?"' 2>/dev/null || echo "?")
            echo "[MEDIUM] sast/opengrep: $check_id in $og_path:$og_line"
          done
        } > "$subtmp/opengrep.findings"
        fi
      fi
      echo "$count" > "$subtmp/opengrep.count"
    ) &
  fi

  wait

  # Collect results from sub-tools
  local total_count=0
  for f in "$subtmp"/*.count; do
    [[ -f "$f" ]] || continue
    c=$(cat "$f" 2>/dev/null || echo "0")
    total_count=$((total_count + c))
  done
  cat "$subtmp"/*.findings > "$tmpdir/layer5.findings" 2>/dev/null || : > "$tmpdir/layer5.findings"

  # Collect SBOM path
  if [[ -f "$subtmp/sbom_path" ]]; then
    cat "$subtmp/sbom_path" > "$tmpdir/sbom_path"
  fi
  # Print SBOM stdout if present
  if [[ -f "$subtmp/sbom.stdout" ]]; then
    cat "$subtmp/sbom.stdout"
  fi

  if [[ "$ran" == true ]]; then
    [[ $total_count -eq 0 ]] && echo "PASS" > "$tmpdir/layer5.status" || echo "WARN" > "$tmpdir/layer5.status"
  else
    echo "SKIP" > "$tmpdir/layer5.status"
  fi
  echo "$total_count" > "$tmpdir/layer5.count"
}

# ========== Launch all 5 layers in parallel ==========
layer1_secrets &
layer2_sast &
layer3_deps &
layer4_infra &
layer5_supply_chain &
wait

# ========== Collect results from temp files ==========
layer1_status=$(cat "$tmpdir/layer1.status" 2>/dev/null || echo "SKIP")
layer1_count=$(cat "$tmpdir/layer1.count" 2>/dev/null || echo "0")
layer2_status=$(cat "$tmpdir/layer2.status" 2>/dev/null || echo "SKIP")
layer2_count=$(cat "$tmpdir/layer2.count" 2>/dev/null || echo "0")
layer3_status=$(cat "$tmpdir/layer3.status" 2>/dev/null || echo "SKIP")
layer3_count=$(cat "$tmpdir/layer3.count" 2>/dev/null || echo "0")
layer4_status=$(cat "$tmpdir/layer4.status" 2>/dev/null || echo "SKIP")
layer4_count=$(cat "$tmpdir/layer4.count" 2>/dev/null || echo "0")
layer5_status=$(cat "$tmpdir/layer5.status" 2>/dev/null || echo "SKIP")
layer5_count=$(cat "$tmpdir/layer5.count" 2>/dev/null || echo "0")
sbom_path=$(cat "$tmpdir/sbom_path" 2>/dev/null || echo "")

# Collect all findings into a single array
declare -a FINDINGS=()
for layer_num in 1 2 3 4 5; do
  findings_file="$tmpdir/layer${layer_num}.findings"
  if [[ -f "$findings_file" ]] && [[ -s "$findings_file" ]]; then
    mapfile -t temp_findings < <(grep -v '^$' "$findings_file")
    FINDINGS+=("${temp_findings[@]}")
  fi
done

# ========== Output Report ==========
layer1_detail="$layer1_status"
[[ "$layer1_status" == "WARN" ]] && layer1_detail="WARN ($layer1_count findings)"
[[ "$layer1_status" == "SKIP" ]] && layer1_detail="SKIP (tool unavailable)"

layer2_detail="$layer2_status"
[[ "$layer2_status" == "WARN" ]] && layer2_detail="WARN ($layer2_count findings)"
[[ "$layer2_status" == "SKIP" ]] && layer2_detail="SKIP (tool unavailable)"

layer3_detail="$layer3_status"
[[ "$layer3_status" == "WARN" ]] && layer3_detail="WARN ($layer3_count findings)"
[[ "$layer3_status" == "SKIP" ]] && layer3_detail="SKIP (tool unavailable)"

layer4_detail="$layer4_status"
[[ "$layer4_status" == "WARN" ]] && layer4_detail="WARN ($layer4_count findings)"
[[ "$layer4_status" == "SKIP" ]] && layer4_detail="SKIP (tool unavailable)"

layer5_detail="$layer5_status"
[[ "$layer5_status" == "WARN" ]] && layer5_detail="WARN ($layer5_count findings)"
[[ "$layer5_status" == "SKIP" ]] && layer5_detail="SKIP (tool unavailable)"

total_findings=$((layer1_count + layer2_count + layer3_count + layer4_count + layer5_count))

# P5.4: Track critical findings — secrets detected means fail-closed (exit 2)
_security_critical=0
if [[ "$layer1_status" == "WARN" ]] && [[ "$layer1_count" -gt 0 ]]; then
  _security_critical=1
fi

echo ""
echo "Security Pipeline Report"
echo "========================"
echo "Layer 1 - Secrets:        $layer1_detail"
echo "Layer 2 - SAST:           $layer2_detail"
echo "Layer 3 - Dependencies:   $layer3_detail"
echo "Layer 4 - Infrastructure: $layer4_detail"
echo "Layer 5 - Supply Chain:  $layer5_detail"

if [[ $total_findings -gt 0 ]]; then
  echo ""
  for finding in "${FINDINGS[@]}"; do
    echo "$finding"
  done
fi

# ========== Write JSON results ==========
mkdir -p "$(dirname "$RESULTS_FILE")"

findings_json="["
first=true
for finding in "${FINDINGS[@]}"; do
  severity=$(echo "$finding" | grep -oE '^\[(HIGH|MEDIUM|LOW)\]' 2>/dev/null || echo "[INFO]")
  severity="${severity//[\[\]]/}"
  category=$(echo "$finding" | sed 's/^\[[^]]*\] \([^:]*\):.*/\1/' 2>/dev/null || echo "unknown")
  message=$(echo "$finding" | sed 's/^\[[^]]*\] [^:]*: //' 2>/dev/null || echo "$finding")
  if [[ "$first" == true ]]; then
    first=false
  else
    findings_json+=","
  fi
  message="${message//\\/\\\\}"
  message="${message//\"/\\\"}"
  findings_json+="{\"severity\":\"$severity\",\"category\":\"$category\",\"message\":\"$message\"}"
done
findings_json+="]"

sbom_json=""
if [[ -n "$sbom_path" ]]; then
  sbom_json="\"sbom\": \"$sbom_path\","
fi

cat > "$RESULTS_FILE" <<EJSON
{
  "timestamp": "$now",
  "project": "$PROJECT_DIR",
  ${sbom_json}
  "layers": ["secrets", "sast", "deps", "infra", "supply_chain"],
  "summary": {
    "layer1_secrets": {"status": "$layer1_status", "count": $layer1_count},
    "layer2_sast": {"status": "$layer2_status", "count": $layer2_count},
    "layer3_deps": {"status": "$layer3_status", "count": $layer3_count},
    "layer4_infra": {"status": "$layer4_status", "count": $layer4_count},
    "layer5_supply_chain": {"status": "$layer5_status", "count": $layer5_count},
    "total_findings": $total_findings
  },
  "findings": $findings_json
}
EJSON

# P5.4: Exit 2 (fail-closed) when secrets are detected (layer 1 findings > 0)
_sec_exit_rc=0
if [[ "$_security_critical" -eq 1 ]]; then
  echo "SECURITY-PIPELINE FAIL: $layer1_count secret(s) detected in layer 1 -- fail-closed" >&2
  _sec_exit_rc=2
fi

# --- Cache write — store result keyed on HEAD SHA ---
hook_cache_write "$_sec_cache_key" "$_sec_exit_rc" ""
# Ultra-fast cache for next time
mkdir -p "$_CACHE_DIR" 2>/dev/null || true
echo "" > "$_CACHE_FILE" 2>/dev/null || true

exit "$_sec_exit_rc"
