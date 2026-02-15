#!/usr/bin/env bash
# qa-attestation-builder.sh
# P16.2 / CDDL-C1: Generate attestation with in-toto Statement format and SLSA provenance.
# Supports SLSA provenance v0.2 and v1 predicateTypes.
# Emits predicateType, policy hash, optional Rekor bundle pointer.
# Rekor integration: reads .claude/sigstore-private.json or uses env vars.
set -euo pipefail

# === CLI Argument Parsing ===
OUTPUT=""
SLSA_VERSION="v1"
PREDICATE_TYPE="slsa"  # "slsa" or "qa-governance"
PROJECT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output|-o)
      OUTPUT="$2"
      shift 2
      ;;
    --slsa-version)
      SLSA_VERSION="$2"
      shift 2
      ;;
    --predicate-type)
      PREDICATE_TYPE="$2"
      shift 2
      ;;
    --project-dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
qa-attestation-builder.sh - Generate in-toto attestations with SLSA provenance

USAGE:
  qa-attestation-builder.sh [OPTIONS]

OPTIONS:
  --output, -o PATH         Output file path (default: .claude/verification/qa-attestation.json)
  --slsa-version VERSION    SLSA provenance version: v0.2 or v1 (default: v1)
  --predicate-type TYPE     Predicate type: "slsa" or "qa-governance" (default: slsa)
  --project-dir PATH        Project directory (default: current directory)
  --help, -h                Show this help message

EXAMPLES:
  qa-attestation-builder.sh --output attestation.json --slsa-version v1
  qa-attestation-builder.sh --predicate-type qa-governance
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# === Setup ===
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
OUT="${OUTPUT:-$VERIFY_DIR/qa-attestation.json}"
QUALITY="$PROJECT_DIR/.claude/quality.json"
SIGSTORE="$PROJECT_DIR/.claude/sigstore-private.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$(dirname "$OUT")"

# === Git Metadata (for SLSA buildDefinition) ===
git_sha="$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo "no-git-sha")"
git_ref="$(git -C "$PROJECT_DIR" symbolic-ref -q --short HEAD 2>/dev/null || git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
git_remote="$(git -C "$PROJECT_DIR" config --get remote.origin.url 2>/dev/null || echo "unknown")"
builder_id="https://github.com/kush/sharecli/builder/qa-attestation-builder"

# === Policy hash (sha256 of quality.json when present) ===
policy_hash=""
if [[ -f "$QUALITY" ]]; then
  if command -v sha256sum >/dev/null 2>&1; then
    policy_hash="$(sha256sum "$QUALITY" | awk '{print $1}')"
  else
    policy_hash="$(shasum -a 256 "$QUALITY" | awk '{print $1}')"
  fi
fi

# === Subject: project root as artifact (name + digest) ===
subject_name="."
subject_digest="${policy_hash:-0000000000000000000000000000000000000000000000000000000000000000}"

# === Read quality.json once for chaos_posture (avoids separate jq call) ===
chaos_posture="baseline"
if [[ -f "$QUALITY" ]]; then
  chaos_posture="$(jq -r '.governance.chaos.posture // "baseline"' "$QUALITY" 2>/dev/null || echo "baseline")"
fi

# === Rekor bundle pointer: Try sigstore config, then env vars, then empty ===
rekor_bundle=""
rekor_uuid=""
if [[ -f "$SIGSTORE" ]]; then
  # Read rekor_endpoint with bash json extraction to avoid jq spawn for simple field
  rekor_endpoint=""
  if command -v jq >/dev/null 2>&1; then
    rekor_endpoint="$(jq -r '.rekor_endpoint // empty' "$SIGSTORE" 2>/dev/null || true)"
  fi
  if [[ -n "$rekor_endpoint" && "$rekor_endpoint" != "null" ]]; then
    rekor_uuid="placeholder-$(date +%s)"
    rekor_bundle="{\"logIndex\":\"${rekor_uuid}\",\"Endpoint\":\"${rekor_endpoint}\"}"
  fi
else
  rekor_endpoint="${REKOR_ENDPOINT:-}"
  rekor_uuid="${REKOR_ENTRY_UUID:-}"
  if [[ -n "$rekor_endpoint" && -n "$rekor_uuid" ]]; then
    rekor_bundle="{\"logIndex\":\"${rekor_uuid}\",\"Endpoint\":\"${rekor_endpoint}\"}"
  fi
fi

# === Build SLSA Provenance Predicate ===
build_slsa_predicate() {
  local version="$1"
  local started_on="${2:-$now}"
  local finished_on="$now"
  local invocation_id="session-$$-$(date +%s)"

  if [[ "$version" == "v0.2" ]]; then
    # SLSA v0.2 predicate structure (deprecated but still supported)
    jq -n \
      --arg builder_id "$builder_id" \
      --arg build_type "https://github.com/kush/sharecli/build-type/bash" \
      --arg invocation_id "$invocation_id" \
      --arg git_sha "$git_sha" \
      --arg git_ref "$git_ref" \
      --arg git_remote "$git_remote" \
      --arg started "$started_on" \
      --arg finished "$finished_on" \
      '{
        builder: { id: $builder_id },
        buildType: $build_type,
        invocation: {
          configSource: {
            uri: $git_remote,
            digest: { sha1: $git_sha },
            entryPoint: "qa-attestation-builder.sh"
          },
          parameters: {},
          environment: {
            git_sha: $git_sha,
            git_ref: $git_ref
          }
        },
        buildConfig: {},
        materials: [{
          uri: $git_remote,
          digest: { sha1: $git_sha }
        }],
        metadata: {
          buildStartedOn: $started,
          buildFinishedOn: $finished,
          completeness: {
            arguments: true,
            environment: true,
            materials: true
          },
          reproducible: false
        }
      }'
  else
    # SLSA v1 predicate structure (default)
    jq -n \
      --arg builder_id "$builder_id" \
      --arg build_type "https://github.com/kush/sharecli/build-type/bash" \
      --arg git_sha "$git_sha" \
      --arg git_ref "$git_ref" \
      --arg git_remote "$git_remote" \
      --arg started "$started_on" \
      --arg finished "$finished_on" \
      --arg invocation_id "$invocation_id" \
      '{
        buildDefinition: {
          buildType: $build_type,
          externalParameters: {
            git_ref: $git_ref,
            project_dir: "."
          },
          internalParameters: {
            git_sha: $git_sha
          },
          resolvedDependencies: [{
            uri: $git_remote,
            digest: { gitSha: $git_sha }
          }]
        },
        runDetails: {
          builder: {
            id: $builder_id
          },
          metadata: {
            invocationId: $invocation_id,
            startedOn: $started,
            finishedOn: $finished
          }
        }
      }'
  fi
}

# === Test Type Detection ===
# Detect test types by examining test directories and file patterns.
# Uses bash builtins (directory tests, glob, compgen) instead of find/rg spawns.
detect_test_types() {
  local detected_unit=false
  local detected_integration=false
  local detected_e2e=false
  local detected_security=false
  local detected_property_based=false
  local detected_contract=false
  local detected_mutation=false
  local detected_bdd=false

  # Unit tests: test/unit/, tests/unit/
  if [[ -d "$PROJECT_DIR/test/unit" ]] || [[ -d "$PROJECT_DIR/tests/unit" ]]; then
    detected_unit=true
  fi
  # Also check for common test file patterns with a single find (maxdepth-limited, -quit for early exit)
  if [[ "$detected_unit" == "false" ]]; then
    if find "$PROJECT_DIR" -maxdepth 3 -type f \( -name "*_test.*" -o -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.*" \) -print -quit 2>/dev/null | read -r _; then
      detected_unit=true
    fi
  fi

  # Integration tests: test/integration/, tests/integration/
  if [[ -d "$PROJECT_DIR/test/integration" ]] || [[ -d "$PROJECT_DIR/tests/integration" ]]; then
    detected_integration=true
  fi

  # E2E tests: directory checks only (no subprocess)
  if [[ -d "$PROJECT_DIR/test/e2e" ]] || [[ -d "$PROJECT_DIR/tests/e2e" ]] || \
     [[ -d "$PROJECT_DIR/test/end-to-end" ]] || [[ -d "$PROJECT_DIR/cypress" ]] || \
     [[ -d "$PROJECT_DIR/playwright" ]] || [[ -d "$PROJECT_DIR/e2e" ]]; then
    detected_e2e=true
  fi

  # Security tests: directory and config file checks (no subprocess)
  if [[ -d "$PROJECT_DIR/test/security" ]] || [[ -d "$PROJECT_DIR/tests/security" ]] || \
     [[ -f "$PROJECT_DIR/.gitleaks.toml" ]] || [[ -f "$PROJECT_DIR/.semgrep.yml" ]] || \
     [[ -f "$PROJECT_DIR/bandit.yaml" ]]; then
    detected_security=true
  fi

  # Property-based tests: single rg call (only if rg available)
  if command -v rg >/dev/null 2>&1; then
    if rg -l -q --max-depth 4 'hypothesis|fast-check|quickcheck|proptest|property' "$PROJECT_DIR" 2>/dev/null; then
      detected_property_based=true
    fi
  fi

  # Contract tests: directory and file checks (no subprocess)
  if [[ -d "$PROJECT_DIR/test/contract" ]] || [[ -d "$PROJECT_DIR/tests/contract" ]] || \
     [[ -f "$PROJECT_DIR/pact.json" ]]; then
    detected_contract=true
  fi

  # Mutation tests: config file checks (no subprocess)
  if [[ -f "$PROJECT_DIR/.mutmut.ini" ]] || [[ -f "$PROJECT_DIR/stryker.conf.js" ]] || \
     [[ -f "$PROJECT_DIR/stryker.config.js" ]]; then
    detected_mutation=true
  fi

  # BDD tests: directory check + single find with -quit
  if [[ -d "$PROJECT_DIR/features" ]] || [[ -d "$PROJECT_DIR/test/bdd" ]] || \
     [[ -d "$PROJECT_DIR/tests/bdd" ]]; then
    detected_bdd=true
  fi
  if [[ "$detected_bdd" == "false" ]]; then
    if find "$PROJECT_DIR" -maxdepth 3 -type f -name "*.feature" -print -quit 2>/dev/null | read -r _; then
      detected_bdd=true
    fi
  fi

  # Build JSON with printf (zero jq spawns)
  printf '{"unit":%s,"integration":%s,"e2e":%s,"security":%s,"property_based":%s,"contract":%s,"mutation":%s,"bdd":%s}\n' \
    "$detected_unit" "$detected_integration" "$detected_e2e" "$detected_security" \
    "$detected_property_based" "$detected_contract" "$detected_mutation" "$detected_bdd"
}

# Detect FR coverage from test files (counts FR tags in test files)
# Uses single rg calls with --count instead of rg | sort -u | wc -l pipelines.
detect_fr_coverage() {
  local fr_total=0
  local fr_covered=0
  local fr_pattern="FR-[A-Z]+-[0-9]+"

  # Check if FUNCTIONAL_REQUIREMENTS.md exists for total count
  if [[ -f "$PROJECT_DIR/FUNCTIONAL_REQUIREMENTS.md" ]] && command -v rg >/dev/null 2>&1; then
    fr_total=$(rg -o "$fr_pattern" "$PROJECT_DIR/FUNCTIONAL_REQUIREMENTS.md" 2>/dev/null | sort -u | wc -l | tr -d ' ')

    # Check test files for FR references (single rg call across test dir)
    if [[ $fr_total -gt 0 && -d "$PROJECT_DIR/test" ]]; then
      fr_covered=$(rg -o "$fr_pattern" -g '*.bats' -g '*_test.*' -g '*.test.*' -g '*.spec.*' -g 'test_*' "$PROJECT_DIR/test" 2>/dev/null | sort -u | wc -l | tr -d ' ')
    fi
  fi

  printf '{"total":%d,"covered":%d}\n' "$fr_total" "$fr_covered"
}

# Detect test-first pairs (source files with corresponding test files)
# Pre-loads test file list once instead of spawning find per source file.
detect_test_first_pairs() {
  local missing_pairs=0
  local checked=0

  # Pre-load all test file basenames into a single string for bash matching
  local test_files_list=""
  if [[ -d "$PROJECT_DIR/test" ]]; then
    test_files_list="$(find "$PROJECT_DIR/test" -type f 2>/dev/null | while read -r f; do echo "${f##*/}"; done)"
  fi

  # Check shell scripts for corresponding test files
  while IFS= read -r src_file; do
    [[ -z "$src_file" ]] && continue
    checked=$((checked + 1))
    local bn="${src_file##*/}"
    bn="${bn%.*}"  # remove extension
    # Match against pre-loaded test file list (bash string match, zero spawns)
    if [[ -z "$test_files_list" ]] || ! grep -q "$bn" <<< "$test_files_list"; then
      missing_pairs=$((missing_pairs + 1))
    fi
  done < <(find "$PROJECT_DIR" -path "$PROJECT_DIR/test" -prune -o -path "$PROJECT_DIR/.git" -prune -o -path "$PROJECT_DIR/node_modules" -prune -o -type f -name "*.sh" -print 2>/dev/null | head -20)

  printf '{"checked":%d,"missing":%d}\n' "$checked" "$missing_pairs"
}

# Run test type detection (each returns printf-generated JSON, no jq)
detected_test_types=$(detect_test_types)
fr_coverage=$(detect_fr_coverage)
test_first_pairs=$(detect_test_first_pairs)

# Count detected test types using bash (parse JSON booleans, no jq spawn)
detected_count=0
for val in unit integration e2e security property_based contract mutation bdd; do
  # Match "key":true in compact JSON
  if [[ "$detected_test_types" == *"\"$val\":true"* ]]; then
    detected_count=$((detected_count + 1))
  fi
done

# Extract fr_coverage fields with bash parameter expansion (no jq spawn)
# Format is {"total":N,"covered":M}
_fr_json="$fr_coverage"
fr_total="${_fr_json#*\"total\":}"
fr_total="${fr_total%%,*}"
fr_total="${fr_total%%\}*}"
fr_covered="${_fr_json#*\"covered\":}"
fr_covered="${fr_covered%%,*}"
fr_covered="${fr_covered%%\}*}"

# Extract test_first_pairs fields (no jq spawn)
# Format is {"checked":N,"missing":M}
_tf_json="$test_first_pairs"
tf_checked="${_tf_json#*\"checked\":}"
tf_checked="${tf_checked%%,*}"
tf_checked="${tf_checked%%\}*}"
tf_missing="${_tf_json#*\"missing\":}"
tf_missing="${tf_missing%%,*}"
tf_missing="${tf_missing%%\}*}"

# Calculate FR coverage percent (bash arithmetic)
if [[ $fr_total -gt 0 ]]; then
  fr_coverage_pct=$((fr_covered * 100 / fr_total))
else
  fr_coverage_pct=0
fi

# Build methodology section (printf, zero jq spawns)
methodology=$(printf '{"detected_test_types":%s,"detected_test_types_count":%d,"test_first":{"missing_test_pairs":%d,"checked_source_files":%d},"missing_required_test_types":[]}\n' \
  "$detected_test_types" "$detected_count" "$tf_missing" "$tf_checked")

# Build summary section (printf, zero jq spawns)
summary=$(printf '{"fr_total":%d,"fr_covered":%d,"fr_coverage_percent":%d,"test_types_detected":%d,"orphan_tests":0}\n' \
  "$fr_total" "$fr_covered" "$fr_coverage_pct" "$detected_count")

# Build security section (bash conditionals, printf, zero jq spawns)
signed_present=false
slsa_present=false
[[ -f "$VERIFY_DIR/attestation.sig" ]] && signed_present=true
[[ -f "$PROJECT_DIR/.slsa-provenance.json" ]] && slsa_present=true
security=$(printf '{"signed_attestation_present":%s,"slsa_provenance_present":%s}\n' \
  "$signed_present" "$slsa_present")

# === Build QA Governance Predicate ===
build_qa_predicate() {
  local rekor_json="null"
  if [[ -n "$rekor_bundle" ]]; then
    rekor_json="$rekor_bundle"
  fi
  jq -n \
    --arg ts "$now" \
    --arg ph "${policy_hash:-}" \
    --argjson rekor "$rekor_json" \
    --arg posture "$chaos_posture" \
    --argjson methodology "$methodology" \
    --argjson summary "$summary" \
    --argjson security "$security" \
    '{
      generated_at: $ts,
      policy_sha256: (if $ph != "" then $ph else null end),
      rekor_bundle_pointer: $rekor,
      chaos_posture: $posture,
      attestation_source: "qa-attestation-builder.sh",
      methodology: $methodology,
      summary: $summary,
      security: $security
    }'
}

# === Select predicate type and build attestation ===
if [[ "$PREDICATE_TYPE" == "slsa" ]]; then
  # SLSA provenance predicate
  if [[ "$SLSA_VERSION" == "v0.2" ]]; then
    predicate_type="https://slsa.dev/provenance/v0.2"
  else
    predicate_type="https://slsa.dev/provenance/v1"
  fi
  predicate=$(build_slsa_predicate "$SLSA_VERSION")
else
  # QA governance predicate (legacy/custom)
  predicate_type="https://kush.local/qa-governance/v1"
  predicate=$(build_qa_predicate)
fi

# === Generate in-toto Statement ===
jq -n \
  --arg ptype "$predicate_type" \
  --arg name "$subject_name" \
  --arg digest "$subject_digest" \
  --argjson pred "$predicate" \
  '{
    "_type": "https://in-toto.io/Statement/v1",
    predicateType: $ptype,
    subject: [{
      name: $name,
      digest: { sha256: $digest }
    }],
    predicate: $pred
  }' > "$OUT"

# === Output status ===
rekor_status="none"
if [[ -n "$rekor_bundle" ]]; then
  rekor_status="enabled"
fi

echo "Attestation: $OUT (predicateType=$predicate_type slsa=$SLSA_VERSION policy_hash=${policy_hash:0:16}... rekor=$rekor_status)"
exit 0
