#!/usr/bin/env bash
# Repos from KOOSHPARI_STALE_TRIAGE_REMAINING_2026-03-29.tsv where proposed_action=archive_github
# Review before run: gh auth, org admin where required.
set -euo pipefail
ORG="${GITHUB_ORG:-KooshaPari}"
for repo in PriceyApp pheno-sdk netweave-final2 agslag-dash Byteport-TestZip; do
  echo "Archiving ${ORG}/${repo} ..."
  gh repo archive "${ORG}/${repo}" --yes || echo "SKIP/FAIL: ${repo}"
done
