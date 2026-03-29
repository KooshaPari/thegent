# Secrets, MiniMax/CLIProxy harnesses, and cross-site mesh — runbook

**Date**: 2026-03-29  
**AgilePlus**: `secrets-mesh-minimax-harness` (`AgilePlus/kitty-specs/secrets-mesh-minimax-harness/spec.md`)

## P0 — You must still do (no automation)

1. **Rotate** any MiniMax (and other) keys that were ever pasted into chat or committed.
2. **Put the new MiniMax key** into sops (`~/.local/state/phenotype/secrets/secrets.env.age` by default) or `export MINIMAX_API_KEY=...`, or Vault KV `secret/phenotype/minimax` field `api_key`.
3. **Re-enter** other BYOK keys in Factory / CLIProxy (repo `.factory/*.json` uses empty `apiKey` for scrubbed slots).

## One-command local scaffolding

```bash
bash "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/phenotype_secrets_init.sh"
```

Creates `~/.local/state/phenotype/secrets/` plus `secrets.env.in` from the template. Encrypt with sops per `thegent/templates/secrets/sops-phenotype-config.yaml.example`.

## Shell harness

Source from `~/.zshrc.local` (see prior setup) or:

```bash
. "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/phenotype_minimax_harness.sh"
```

Functions: `mclaude`, `mcodex`, `vclaude`, `vcodex`, `phenotype_harness_unload`. PowerShell: `phenotype_minimax_harness.ps1`.

Default model: `minimax-m2.7-highspeed` (`PHENOTYPE_MINIMAX_MODEL` overrides).

## CLIProxy + adapter

```bash
bash "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/cliproxy_adapter_up.sh"
```

Uses `thegent mcp up` when installed; otherwise searches for `scripts/start_proxy_with_adapter.py` + `uv`. **Codex** needs `/v1/responses` — keep `THGENT_CLIPROXY_ADAPTER=1`.

**URLs**: `http://127.0.0.1:8317/v1` (include `/v1`).

Canonical docs: `thegent/docs/research/CODEX_CLIPROXY_CONFIG_AUDIT_AND_PLAN.md`, `thegent/docs/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md`, `thegent/docs/guides/PROVIDER_SETUP_GUIDE.md`.

MiniMax coding-plan: `https://platform.minimax.io/docs/coding-plan/claude-code`, `https://platform.minimax.io/docs/coding-plan/codex-cli`

## Tailnet (AZ ↔ LA)

- Example ACL (edit before use): `thegent/templates/tailnet/tailscale-acl.hujson.example`
- **Tailscale**: paste ACL in admin console; use tags for `laptop` vs `home` nodes.
- **Headscale** (self-hosted control plane): run on a small Linux VM (**OrbStack** on Mac, or WSL2/VPS). Follow [headscale.net](https://headscale.net) install; join nodes with the same ACL concepts (destination ports 22, 8317, 8200 as needed).

## GitHub Actions → Vault (template)

Copy `thegent/templates/github/workflows/vault-oidc-example.yml` into a repo’s `.github/workflows/` after configuring Vault JWT auth and a GitHub OIDC role. **Do not** enable until Vault policy is correct.

## Verification

- [ ] `git grep -E 'sk-cp-|api_key.:\"[^\"]{20,}\"'` clean in tracked config (except dummy placeholders).
- [ ] `mclaude` works after sops/env key set.
- [ ] Adapter up; `curl -s http://127.0.0.1:8317/v1/models | head` succeeds.
- [ ] `vcodex` smoke with Codex CLI.

## Resource expectations

No cross-WAN RAM/GPU “RAID”. Use job routing (SSH/tailnet), sync (Syncthing/restic), and separate display/session planes.
