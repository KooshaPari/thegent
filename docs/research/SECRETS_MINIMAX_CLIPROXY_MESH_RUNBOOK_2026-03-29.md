# MiniMax/CLIProxy harnesses and cross-site mesh — runbook

**Date**: 2026-03-29  
**AgilePlus**: `secrets-mesh-minimax-harness` (`AgilePlus/kitty-specs/secrets-mesh-minimax-harness/spec.md`)  
**Invariant prose**: [`docs/reference/CANONICAL_INVARIANT_PROSE.md`](../reference/CANONICAL_INVARIANT_PROSE.md) (use `CredentialRef::*` / `ModelRef::*` in specs; Vale vocabulary)

## Policy (ZDR + BYOK)

- **ZDR** (zero data retention) on provider harnesses may make **scheduled credential rotation** unnecessary for those routes; follow org policy, not generic “rotate everything” checklists.
- **Factory** does **not** issue provider keys; it stores **BYOK** credential material you supply in `custom_models` / `customModels`.
- Canonical MiniMax model id: **`ModelRef::MINIMAX_M27_HS`** → `minimax-m2.7-highspeed` unless your CLIProxy catalog differs.

## Optional: shell-only `CredentialRef::MINIMAX_BYOK`

If you do **not** rely on Factory JSON for env exports, supply `MINIMAX_API_KEY` via SOPS or Vault — see `thegent/scripts/shell/phenotype_minimax_harness.sh`. Factory users can skip this when BYOK is already in `~/.factory` / `repos/.factory`.

## One-command local scaffolding (optional)

```bash
bash "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/phenotype_secrets_init.sh"
```

## Shell harness

```bash
. "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/phenotype_minimax_harness.sh"
```

Functions: `mclaude`, `mcodex`, `vclaude`, `vcodex`, `phenotype_harness_unload`. PowerShell: `phenotype_minimax_harness.ps1`.

## CLIProxy + adapter

```bash
bash "$HOME/CodeProjects/Phenotype/repos/thegent/scripts/shell/cliproxy_adapter_up.sh"
```

**Codex** needs `/v1/responses` — keep `THGENT_CLIPROXY_ADAPTER=1`. **URL**: `EndpointRef::CLIPROXY_V1` → `http://127.0.0.1:8317/v1`.

Docs: `thegent/docs/research/CODEX_CLIPROXY_CONFIG_AUDIT_AND_PLAN.md`, `thegent/docs/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md`, `thegent/docs/guides/PROVIDER_SETUP_GUIDE.md`.

MiniMax coding-plan: `https://platform.minimax.io/docs/coding-plan/claude-code`, `https://platform.minimax.io/docs/coding-plan/codex-cli`

## Tailnet (AZ ↔ LA)

- Example ACL: `thegent/templates/tailnet/tailscale-acl.hujson.example`
- **headscale**: OrbStack VM or WSL2 — see [headscale.net](https://headscale.net).

## GitHub Actions → Vault (template)

`thegent/templates/github/workflows/vault-oidc-example.yml` — copy when Vault JWT is configured.

## Verification

- [ ] Default session model resolves (`custom:minimax-m2.7-byok-3` in sync with `repos/.factory/settings.json`).
- [ ] `mclaude` / `mcodex` or Factory session against MiniMax succeeds.
- [ ] Adapter up; `curl -s http://127.0.0.1:8317/v1/models | head` succeeds.
- [ ] **Model id invariant:** `uv run python scripts/phenotype_cliproxy_models_check.py` (or `uv run python -m thegent.phenotype.cliproxy_models_check`) exits 0 and reports `ModelRef::MINIMAX_M27_HS` / `minimax-m2.7-highspeed` in the catalog. Override base URL with `CLIPROXY_BASE_URL`; optional bearer via `CLIPROXY_MODELS_BEARER` or `OPENAI_API_KEY`. If catalog ids are provider-prefixed, use `CLIPROXY_MODELS_MATCH=substring` or `--match substring` (see [`LANGUAGE_INVARIANTS_AND_VALE_2026-03.md`](LANGUAGE_INVARIANTS_AND_VALE_2026-03.md) § operational check).
- [ ] `vcodex` smoke with Codex CLI.

## Resource expectations

No cross-WAN RAM/GPU “RAID”. Use job routing (SSH/tailnet), sync (Syncthing/restic), separate display/session planes.
