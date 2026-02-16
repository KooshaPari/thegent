#!/usr/bin/env bash
# qa-supply-chain-verifier.sh
# Verifies signed attestation and provenance requirements (cosign/Rekor aware).
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_FILE="${_CACHE_DIR}/supply-chain-${_CACHE_KEY}.result"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < _CACHE_TTL )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

HOOK_NAME="QA-SUPPLY-CHAIN-VERIFIER"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# --- Cache check — skip if unchanged within TTL ---
_sc_cache_key="${HOOK_NAME}_${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}"
_sc_ttl="${HOOK_CACHE_TTL:-600}"
if hook_cache_check "$_sc_cache_key" "$_sc_ttl"; then
  hook_cache_read "$_sc_cache_key" | tee "$_CACHE_FILE" 2>/dev/null
  _cached_rc=$?
  if [[ "$_cached_rc" -ne 0 ]]; then
    echo "QA-SUPPLY-CHAIN-VERIFIER FAIL: cached result was non-zero ($_cached_rc)" >&2
  fi
  exit "$_cached_rc"
fi

ATTEST="$VERIFY_DIR/qa-attestation.json"
SIG="$VERIFY_DIR/qa-attestation.sig"
BUNDLE="$VERIFY_DIR/qa-attestation.bundle.json"
REPORT="$VERIFY_DIR/supply-chain-report.json"

REQUIRE_SIGNED="${QA_REQUIRE_SIGNED_ATTESTATION:-false}"
REQUIRE_SLSA="${QA_REQUIRE_SLSA_PROVENANCE:-false}"
REQUIRE_REKOR="${QA_REQUIRE_REKOR_VERIFICATION:-false}"
FAIL_CLOSED="${QA_SUPPLY_CHAIN_FAIL_CLOSED:-true}"
COSIGN_KEY="${QA_COSIGN_PUBLIC_KEY:-}"
COSIGN_CERT="${QA_COSIGN_CERT:-}"
COSIGN_IDENTITY="${QA_COSIGN_IDENTITY:-}"
COSIGN_ISSUER="${QA_COSIGN_ISSUER:-}"

if [[ -f "$QUALITY_CONFIG" ]] && command -v "${JQ_CMD:-jq}" >/dev/null 2>&1; then
  tier="$("${JQ_CMD:-jq}" -r '.criticality_tier // "established"' "$QUALITY_CONFIG" 2>/dev/null || echo established)"
  if [[ "$tier" == "critical" ]]; then
    REQUIRE_SIGNED="${QA_REQUIRE_SIGNED_ATTESTATION:-true}"
    REQUIRE_SLSA="${QA_REQUIRE_SLSA_PROVENANCE:-true}"
    REQUIRE_REKOR="${QA_REQUIRE_REKOR_VERIFICATION:-true}"
  fi
fi

errors=()
warns=()
cosign_used=false
cosign_verified=false
rekor_verified=false
slsa_present=false
signed_present=false

if [[ -f "$ATTEST" ]]; then
  slsa_present=true
fi
if [[ -f "$SIG" ]]; then
  signed_present=true
fi

if [[ "$REQUIRE_SLSA" == "true" && "$slsa_present" != "true" ]]; then
  errors+=("required attestation file missing: $ATTEST")
fi

if [[ "$REQUIRE_SIGNED" == "true" && "$signed_present" != "true" ]]; then
  errors+=("required signature file missing: $SIG")
fi

if [[ "$signed_present" == "true" ]]; then
  if command -v cosign >/dev/null 2>&1; then
    cosign_used=true
    if [[ -n "$COSIGN_KEY" ]]; then
      if cosign verify-blob --key "$COSIGN_KEY" --signature "$SIG" "$ATTEST" >/dev/null 2>&1; then
        cosign_verified=true
      else
        errors+=("cosign key verification failed")
      fi
    elif [[ -n "$COSIGN_CERT" ]]; then
      cmd=(cosign verify-blob --certificate "$COSIGN_CERT" --signature "$SIG")
      [[ -n "$COSIGN_IDENTITY" ]] && cmd+=(--certificate-identity-regexp "$COSIGN_IDENTITY")
      [[ -n "$COSIGN_ISSUER" ]] && cmd+=(--certificate-oidc-issuer-regexp "$COSIGN_ISSUER")
      cmd+=("$ATTEST")
      if "${cmd[@]}" >/dev/null 2>&1; then
        cosign_verified=true
      else
        errors+=("cosign certificate verification failed")
      fi
    else
      warns+=("signature exists but no cosign verification material configured (QA_COSIGN_PUBLIC_KEY or QA_COSIGN_CERT)")
      [[ "$REQUIRE_SIGNED" == "true" ]] && errors+=("signed attestation required, but verification material not configured")
    fi
  else
    warns+=("cosign not installed")
    [[ "$REQUIRE_SIGNED" == "true" ]] && errors+=("signed attestation required, but cosign is unavailable")
  fi
fi

if [[ "$REQUIRE_REKOR" == "true" ]]; then
  if [[ ! -f "$BUNDLE" ]]; then
    errors+=("Rekor verification required but bundle missing: $BUNDLE")
  elif [[ "$cosign_used" == "true" && "$cosign_verified" == "true" ]]; then
    if cosign verify-blob --bundle "$BUNDLE" --signature "$SIG" "$ATTEST" >/dev/null 2>&1; then
      rekor_verified=true
    else
      errors+=("Rekor bundle verification failed")
    fi
  else
    warns+=("Rekor bundle present but cosign verification not completed")
    errors+=("Rekor verification required but cosign verification path unavailable")
  fi
fi

"${JQ_CMD:-jq}" -n \
  --arg ts "$now" \
  --arg project "$PROJECT_DIR" \
  --argjson require_signed "${REQUIRE_SIGNED}" \
  --argjson require_slsa "${REQUIRE_SLSA}" \
  --argjson require_rekor "${REQUIRE_REKOR}" \
  --argjson slsa_present "$slsa_present" \
  --argjson signed_present "$signed_present" \
  --argjson cosign_used "$cosign_used" \
  --argjson cosign_verified "$cosign_verified" \
  --argjson rekor_verified "$rekor_verified" \
  --argjson errors "$(printf '%s\n' "${errors[@]-}" | sed '/^$/d' | "${JQ_CMD:-jq}" -R . | "${JQ_CMD:-jq}" -s .)" \
  --argjson warns "$(printf '%s\n' "${warns[@]-}" | sed '/^$/d' | "${JQ_CMD:-jq}" -R . | "${JQ_CMD:-jq}" -s .)" \
  '{
    generated_at:$ts,
    project_dir:$project,
    requirements:{signed:$require_signed,slsa:$require_slsa,rekor:$require_rekor},
    observed:{slsa_present:$slsa_present,signed_present:$signed_present,cosign_used:$cosign_used,cosign_verified:$cosign_verified,rekor_verified:$rekor_verified},
    error_count:($errors|length),
    warn_count:($warns|length),
    errors:$errors,
    warns:$warns,
    pass:(($errors|length)==0)
  }' > "$REPORT"

ecount="$("${JQ_CMD:-jq}" '.error_count' "$REPORT")"
wcount="$("${JQ_CMD:-jq}" '.warn_count' "$REPORT")"
_sc_summary="SUPPLY-CHAIN VERIFIER: errors=$ecount warns=$wcount report=$REPORT"
echo "$_sc_summary"

if [[ "$FAIL_CLOSED" == "true" && "$ecount" -gt 0 ]]; then
  _sc_err_detail=$("${JQ_CMD:-jq}" -r '.errors[] | "- " + .' "$REPORT")
  echo "$_sc_err_detail"
  hook_cache_write "$_sc_cache_key" "2" "${_sc_summary}"$'\n'"${_sc_err_detail}"
  # Ultra-fast cache for next time
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  printf '%s\n%s' "$_sc_summary" "$_sc_err_detail" > "$_CACHE_FILE" 2>/dev/null || true
  echo "SUPPLY-CHAIN VERIFIER FAIL: $ecount supply chain error(s) found" >&2
  exit 2
fi

hook_cache_write "$_sc_cache_key" "0" "$_sc_summary"
# Ultra-fast cache for next time
mkdir -p "$_CACHE_DIR" 2>/dev/null || true
echo "$_sc_summary" > "$_CACHE_FILE" 2>/dev/null || true
exit 0
