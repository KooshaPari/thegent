# 17_NEXT_WAVE_K — next 25 items (Waves 1-8 sequence)

**Follows** `07`–`16`. **Snapshot:** 2026-03-24. **Intent:** Security & Compliance.

## Slice 1 — Security Hardening (8)
1. **CSP**: Audit `Content-Security-Policy` for `heliosApp`.
2. **CORS**: Verify strict origin matching for API.
3. **Secrets**: Standardize `dotenv-vault` or `infisical`.
4. **Auth**: Audit JWT `alg` and `exp` claims for all APIs.
5. **Session**: Verify strict `HttpOnly` and `SameSite` for cookies.
6. **TLS**: Audit `curl` or `fetch` for insecure connections.
7. **Rate Limit**: Verify `rack-attack` or `redis` limits.
8. **Sandbox**: Verify `Electron` contextIsolation and sandbox.

## Slice 2 — Compliance & Audit (8)
9. **GDPR**: Audit data retention and deletion for local DBs.
10. **CCPA**: Create 'Right to Forget' handler for PII.
11. **SBOM**: Standardize `cyclonedx` or `spdx` outputs.
12. **Licenses**: Audit all new transitive dependencies.
13. **Vulnerability**: Enable `GitHub Security Advisories`.
14. **Scan**: Run `CodeQL` across the entire org.
15. **Artifacts**: Verify hash-sum checks for all binary downloads.
16. **Updates**: Create a policy for regular security patching.

## Slice 3 — Operational Safety (8)
17. **Kill-Switch**: Test the PTY/secrets/bus emergency shutdown.
18. **Quota**: Implement disk usage quotas for `worktrees`.
19. **Snapshot**: Verify filesystem snapshots for `active` lanes.
20. **Audit**: Review all GHA `permissions:` for least-privilege.
21. **DR**: Test 'Disaster Recovery' restore from backup.
22. **Monitor**: Audit `prometheus` or `datadog` alerting rules.
23. **Incident**: Create an incident response runbook for `helios`.
24. **Change**: Standardize 'Breaking Change' documentation (ADR).

## Slice 4 — Meta (1)
25. **Task Update**: Record security findings in `05_KNOWN_ISSUES.md`.
