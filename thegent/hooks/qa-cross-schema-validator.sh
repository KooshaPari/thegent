#!/usr/bin/env bash
# qa-cross-schema-validator.sh
# PL-014: Cross-schema validation (Requirement <-> Evidence <-> Attestation)
# Ensures that evidence correctly references requirements and attestation covers both.

set -euo pipefail

# Sourcing common hook library if it exists
HOOK_LIB="${0%/*}/lib/common.sh"
if [[ -f "$HOOK_LIB" ]]; then
    source "$HOOK_LIB"
fi

REQ_FILE="${1:-}"
EVIDENCE_FILE="${2:-}"
ATTESTATION_FILE="${3:-}"

if [[ -z "$REQ_FILE" || -z "$EVIDENCE_FILE" || -z "$ATTESTATION_FILE" ]]; then
    echo "Usage: $0 <requirement.json> <evidence.json> <attestation.json>"
    exit 1
fi

if [[ ! -f "$REQ_FILE" ]]; then echo "Error: Requirement file not found: $REQ_FILE"; exit 1; fi
if [[ ! -f "$EVIDENCE_FILE" ]]; then echo "Error: Evidence file not found: $EVIDENCE_FILE"; exit 1; fi
if [[ ! -f "$ATTESTATION_FILE" ]]; then echo "Error: Attestation file not found: $ATTESTATION_FILE"; exit 1; fi

# 1. Extract IDs and Kind
REQ_ID=$(jq -r '.id' "$REQ_FILE")
EVIDENCE_REQ_ID=$(jq -r '.requirement_id // .item_id' "$EVIDENCE_FILE")
EVIDENCE_KIND=$(jq -r '.kind' "$EVIDENCE_FILE")

echo "── Cross-Schema Validation: $REQ_ID ──"

# 2. Linkage Check: Evidence belongs to Requirement
if [[ "$REQ_ID" != "$EVIDENCE_REQ_ID" ]]; then
    echo "  [FAIL] Evidence requirement_id ($EVIDENCE_REQ_ID) does not match requirement id ($REQ_ID)"
    exit 2
fi
echo "  [PASS] Evidence linkage verified"

# 3. Policy Check: Evidence kind satisfies Requirement's evidence_policy
# We check if the evidence kind is listed in the requirement's required evidence
REQUIRED_KINDS=$(jq -r '.evidence_policy.required[]?.kind // empty' "$REQ_FILE")
if [[ -n "$REQUIRED_KINDS" ]]; then
    FOUND=0
    while read -r KIND; do
        if [[ "$KIND" == "$EVIDENCE_KIND" ]]; then
            FOUND=1
            break
        fi
    done <<< "$REQUIRED_KINDS"

    if [[ $FOUND -eq 0 ]]; then
        echo "  [FAIL] Evidence kind ($EVIDENCE_KIND) not found in requirement's required kinds: $REQUIRED_KINDS"
        exit 2
    fi
    echo "  [PASS] Evidence kind ($EVIDENCE_KIND) satisfies policy"
else
    echo "  [FAIL] Requirement is missing evidence_policy.required kinds"
    exit 2
fi

# 4. Attestation Coverage Check
# The attestation should have the requirement and evidence in its subject (by digest)
REQ_DIGEST=$(sha256sum "$REQ_FILE" | awk '{print $1}')
EVIDENCE_DIGEST=$(sha256sum "$EVIDENCE_FILE" | awk '{print $1}')

SUBJECT_DIGESTS=$(jq -r '.subject[].digest.sha256 // empty' "$ATTESTATION_FILE")

if [[ -n "$SUBJECT_DIGESTS" ]]; then
    REQ_COVERED=$(echo "$SUBJECT_DIGESTS" | grep -q "$REQ_DIGEST" && echo "yes" || echo "no")
    EVI_COVERED=$(echo "$SUBJECT_DIGESTS" | grep -q "$EVIDENCE_DIGEST" && echo "yes" || echo "no")

    if [[ "$REQ_COVERED" == "no" ]]; then
        echo "  [FAIL] Attestation does not cover Requirement ($REQ_DIGEST)"
        exit 2
    fi
    if [[ "$EVI_COVERED" == "no" ]]; then
        echo "  [FAIL] Attestation does not cover Evidence ($EVIDENCE_DIGEST)"
        exit 2
    fi
    echo "  [PASS] Attestation coverage verified"
else
    echo "  [FAIL] Attestation has no subject digests"
    exit 2
fi

echo "  [SUCCESS] Cross-schema validation passed for $REQ_ID"
exit 0
