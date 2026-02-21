#!/bin/bash
# Stop hook for harvesting LiteLLM routing metrics.
# Part of Batch E: Routing & QoL tasks.

# Load environment
SESSION_DIR="${THGENT_SESSION_DIR:-${HOME}/.thegent/sessions}"
SESSION_ID="${THGENT_SESSION_ID}"

if [ -z "${SESSION_ID}" ]; then
    echo "LITELLM HARVEST STOP FAIL: THGENT_SESSION_ID not set"
    exit 0 # Don't fail the hook pipeline
fi

# Ensure output directory exists
OUTPUT_DIR="${SESSION_DIR}/${SESSION_ID}"
mkdir -p "${OUTPUT_DIR}"

# Run harvesting via CLI
thegent routing harvest --session-id "${SESSION_ID}" --output "${OUTPUT_DIR}/routing_metrics.json"

if [ $? -eq 0 ]; then
    echo "LITELLM HARVEST STOP SUCCESS: Metrics saved to ${OUTPUT_DIR}/routing_metrics.json"
else
    echo "LITELLM HARVEST STOP FAIL: Harvesting failed"
fi
