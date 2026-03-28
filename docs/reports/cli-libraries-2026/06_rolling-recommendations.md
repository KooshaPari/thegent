# Rust+TypeScript CLI Library Value Matrix and Recommendations (2026)

Last updated: 2026-02-26

## Source inputs (evidence-backed)

- Rust CLI list source: `docs/reports/rust-cli-new-packages-2026/*` (libs.tech Rust CLI list snapshots and follow-on analyses).
- TypeScript/Node CLI scan inputs:
  - `heliosHarness/docs/fragemented/research/phase-1-reports/agent-e-discovery.md`
  - `heliosHarness/research/helios-consolidated.md`

## Scoring heuristics

All package scores are on a 0–100 scale and are intentionally evidence-weighted from the source snapshots.

- **Maintenance (30 pts)**
  - Commit freshness (recency/active branch signal)
  - Issue load and governance signal
  - Release/tooling consistency evidence
- **Fit (35 pts)**
  - Match to shell/ops/productivity workflows captured in the source reports
  - Existing CLI command surface and documented usage patterns
  - Suitability for immediate adoption versus platform-only experimentation
- **Risk (15 pts)**
  - License and security/compliance implications
  - Operational constraints (daemon mode, privilege needs, maintenance caveats)
  - Scope mismatch risk
- **Adoption readiness (20 pts)**
  - Existing ecosystem signals (stars/forks when available)
  - Explicit CLI binary surface and install/run evidence
  - Evidence for stable command behavior

Interpretation rule for each package:

`Total = Maintenance + Fit + Risk + Adoption readiness`

Scores are directional and should be revisited as fresh snapshots arrive.

## 10-100 value matrix

| Package | Language | Maintenance | Fit | Risk | Adoption | Total | Recommendation rationale |
|---|---|---:|---:|---:|---:|---|
| `clap-rs/clap` | Rust | 29 | 34 | 13 | 18 | **94** | Industry-standard parser baseline; strongest foundation for any production Rust CLI command surface. |
| `atuinsh/atuin` | Rust | 25 | 32 | 11 | 17 | **85** | Strong adoption and rich shell-history model; directly matches shell intelligence and AI assistant workflows. |
| `skim-rs/skim` | Rust | 28 | 30 | 12 | 12 | **82** | Very active, low issue load, and strong interactive selection fit for terminal productivity. |
| `bootandy/dust` | Rust | 27 | 29 | 11 | 12 | **79** | Small, mature replacement for `du`-style workflows; low complexity and clear utility. |
| `ducaale/xh` | Rust | 27 | 28 | 11 | 12 | **78** | High-value API-debugging and scriptable HTTP workflow tool; fit for internal ops workflows. |
| `nukesor/pueue` | Rust | 24 | 26 | 12 | 9 | **71** | Useful for durable command orchestration (`add`, `status`, `pause`, `resume`) in queue-based workflows; lower cadence caution. |
| `svenstaro/miniserve` | Rust | 24 | 23 | 10 | 12 | **69** | Lightweight serving utility with clear ops utility; requires external hardening for internet-exposed use. |
| `imsnif/bandwhich` | Rust | 21 | 20 | 9 | 10 | **60** | Strong incident triage utility, but passive maintenance and privileged capture model reduce long-horizon readiness. |
| `Y2Z/monolith` | Rust | 19 | 21 | 9 | 8 | **57** | Good reproducible web snapshot behavior for investigation workflows; slower update cadence and storage/compliance burden. |
| `phiresky/ripgrep-all` | Rust | 18 | 18 | 9 | 8 | **53** | Niche rich search utility with slower cadence and license classifying risk; useful only in targeted use-cases. |
| `claude-code-flow` | TypeScript | 18 | 27 | 12 | 17 | **74** | Explicit Node CLI bin (`claude-flow`) and direct AI-orchestration fit; metrics are limited beyond local scan evidence. |
| `pluggedin-mcp-proxy` | TypeScript | 16 | 22 | 10 | 13 | **61** | Strong command surface (`mcp-cli`, `mcp-simulate`, `mcp-codegen`), narrower fit if MCP-proxy-only is desired. |
| `openai-codex-mcp` | Python (TS scan context) | 14 | 20 | 8 | 14 | **56** | Listed in the TypeScript-oriented candidate scan as Codex wrapper-style interoperability path; not a native TypeScript CLI by package metadata. |

## Shortlist by priority

1. **`clap-rs/clap`** — adopt first as baseline command parser/contract layer for any new Rust CLI work.
2. **`atuinsh/atuin`** and **`nukesor/pueue`** — adopt together for shell-history + job-queue workflows in environments using command-heavy agent orchestration.
3. **`ducaale/xh`** and **`skim-rs/skim`** — adopt for internal API debugging and interactive terminal workflows once policy checks pass.
4. **`claude-code-flow`** — pilot in TypeScript lane as highest-value TS/Node CLI candidate from the gathered scan.

## Recommended stack shape (roll-forward)

- **Core Rust CLI platform:** `clap` + `ducaale/xh` + one of (`atuin` or `pueue`) depending on priority.
- **Interactive productivity extension:** add `skim` only where terminal selection is required.
- **TypeScript interoperability lane:** run a separate proof-of-concept around `claude-code-flow` before any additional TypeScript CLI onboarding.
- **Operational controls:** apply explicit environment allowlists, deterministic output formats, and rollback scripts before broad rollout for `miniserve`, `bandwhich`, and `monolith`.
- **Canonical local-first stack summary:** detailed local-first recommendations for messaging, cache layer, graph database, object storage, and local orchestration now live in [docs/LOCAL_FIRST_INDEX_stack.md](/Users/kooshapari/CodeProjects/Phenotype/repos/docs/LOCAL_FIRST_INDEX_stack.md).

## Risk-aware recommendations

- Treat `bandwhich` and `monolith` as **diagnostic-only** unless runbook controls are in place.
- Treat `pluggedin-mcp-proxy` and `openai-codex-mcp` as **integration-first pilots**, not default platform dependencies.
- Re-score quarterly as upstream commit cadence and license/status signals change.

## Next actions

1. Build a pilot matrix in a sandbox repo with these top 6 picks:
   `clap`, `atuin`, `pueue`, `xh`, `skim`, `claude-code-flow`.
2. Define standardized acceptance checks for each package:
   install/repro, command-level smoke tests, security review gates, and rollback scripts.
3. Re-evaluate scores after 30 days and after one production incident drill to confirm
   maintenance and risk assumptions.
