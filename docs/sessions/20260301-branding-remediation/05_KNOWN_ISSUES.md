# Known Issues

## Policy Baseline (Resolved)

- Canonical GitHub owner is `kooshapari`.
- `Phenotype` is a label/branding term only, not a GitHub org target.
- Canonical cliproxy product brand is `cliproxyapi++`.
- Canonical Helios repo target is `kooshapari/helios-CLI`; legacy no-hyphen references are migration/absorption source text and archive-target markers.

## Remaining Decision-Gated Items

- Package/module identity renames (`go.mod`, `pyproject.toml`, `package.json`) with ecosystem compatibility impact.
- Maintainer/author field normalization policy (keep personal attribution vs team label).
- Legacy product naming transitions (`CLIProxyAPI`, `venture`, `tracertm`, upstream `codex-*`).

## Applied Safe Fixes (Completed)

- Normalized user-specific absolute path references to `$HOME` in selected docs.
- Normalized owner references from `KooshaPari` / `kooshaPari` to `kooshapari` across active docs/config/workflow files.
- Normalized CODEOWNERS/dependabot handle references where present in active remediation scope.
- Added Helios absorption/archival handoff artifacts:
  - `heliosCLI/ARCHIVE_HANDOFF.md`
  - deprecation banner in `heliosCLI/README.md`
  - migration-source warning in `heliosCLI/HELIOSCLI_README.md`
  - canonical-target note in `helios-cli/README.md`
