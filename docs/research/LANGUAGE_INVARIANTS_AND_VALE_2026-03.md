# Language, invariants, and doc tooling (2026)

**Scope:** Controlled vocabulary, lint-time enforcement, and structured-doc patterns for `CredentialRef` / `ModelRef` / `EndpointRef` tokens. **Out of scope here:** provider-specific ZDR contracts (assume org posture separately).

## Vale — vocabularies and term consistency

Vale loads **vocabularies** from `StylesPath/config/vocabularies/<Name>/` (Vale 3+). Setting `Vocab = phenotype` in `.vale.ini` applies `accept.txt` across `BasedOnStyles`, adds spelling exceptions, and drives **`Vale.Terms`** so accepted strings define the canonical casing/spelling.

- Source: [Vale — Vocabularies](https://vale.sh/docs/topics/vocab/)
- Config keys: [`.vale.ini` / Vocab](https://vale.sh/docs/topics/config/)

**Repo wiring:** `styles/config/vocabularies/phenotype/accept.txt` + root `.vale.ini` (`Vocab = phenotype`).

## Stable symbols in Markdown

Backticked code spans (CommonMark **code span** syntax) delimit tokens so linters and search treat them as atomic. Vale’s `TokenIgnores = (`[^`]+`)` skips inline `` `...` `` bodies in this repo’s `.vale.ini`, reducing noise while still allowing headings and prose to use consistent spellings outside spans.

- Source: [CommonMark spec — Code spans](https://spec.commonmark.org/0.31.2/#code-spans)

## LSP — document symbols as “single definition” for humans and tools

The Language Server Protocol’s **`textDocument/documentSymbol`** request exposes a hierarchy of symbols in a document (e.g. headings, functions). Editors use this for outline views and navigation. **Practice:** define each `CredentialRef::*` / `ModelRef::*` once under a dedicated heading and link subsequent sections—mirrors “define once, reference everywhere” without requiring a custom parser.

- Source: [LSP 3.17 — `TextDocument` request `documentSymbol`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol)

## CI / render pipelines — patch step

Substituting manifest- or env-bound values **after** linting authored Markdown matches patterns from Helm values and OpenAPI generators: source docs keep **symbols**; release or site build injects environment-specific endpoints and non-secret metadata. No third-party “AI-LSP” standard is required—**LSP + Vale + a small patch script** cover the same invariants.

## FOL-style predicates (lightweight)

Formal methods toolchains (TLA+, Alloy, etc.) are optional. For **prose-adjacent** specs, a **predicate naming convention** (`HasCredential(x)`, `ModelId(session) = ModelRef::…`) is enough to keep requirements grep-stable and to align tests with doc language. Escalate to real logic languages when you need machine-checked proofs, not for routine runbooks.

## Cross-links

- Canonical vocabulary policy: [`docs/reference/CANONICAL_INVARIANT_PROSE.md`](../reference/CANONICAL_INVARIANT_PROSE.md)
- Mesh/secrets primary sources (orthogonal): [`EXTERNAL_SIGNALS_ZDR_MESH_SECRETS_2026-03.md`](EXTERNAL_SIGNALS_ZDR_MESH_SECRETS_2026-03.md)
