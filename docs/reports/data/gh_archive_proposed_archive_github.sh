#!/usr/bin/env bash
# Generated from KOOSHPARI_STALE_TRIAGE_FULL_2026-03-29.tsv (proposed_action=archive_github only).
# Review each repo, then run with: bash docs/reports/data/gh_archive_proposed_archive_github.sh
# Requires: gh auth, org owner rights. Already-archived repos will error — skip those lines.
set -euo pipefail
ORG="${GITHUB_ORG:-KooshaPari}"
for repo in \
  vibeproxy router-docs P2 472-P2-Flame-War ccusage \
  KDesktopVirt KVirtualStage RIP-Fitness-App kmobile \
  CSE445-A4 localbase-3 localbase-2 netweave-final \
  go-nippon 330p5 Frostify hoohacks \
  340-p2 340P1 odin-dash ssToCal-front canvasApp \
  odin-restaurant Project-Spyn
do
  echo "Archiving ${ORG}/${repo} ..."
  gh repo archive "${ORG}/${repo}" --yes || echo "SKIP/FAIL: ${repo}"
done
