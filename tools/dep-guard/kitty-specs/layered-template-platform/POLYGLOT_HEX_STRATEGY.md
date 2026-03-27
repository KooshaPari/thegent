# Polyglot + Hex Strategy

## Layer Model

1. `template-commons`
- cross-language governance, CI, reconcile semantics.

2. `template-lang-*`
- language-native toolchain contracts and baseline files.

3. `template-domain-*`
- product/domain overlays (webapp, service_api, mobileapp, etc.) that compose commons + one primary language (+ optional secondary).

## Polyglot Factoring

Polyglot projects are composed, not duplicated:

- Primary language layer defines default toolchain.
- Additional language layers are added as optional dependencies in domain compose maps.
- Reconcile uses ownership boundaries to avoid cross-language clobber.

## Hex / Elixir Factoring

`template-lang-elixir-hex` provides:

- Hex/Mix baseline (`mix.exs`).
- Contract-level compatibility with commons governance.
- Domain repos can choose Elixir as primary or optional runtime surface.

## Decision Rules

1. If repo runtime is single-language: depend on one language layer.
2. If repo is polyglot: define primary + optional language layers explicitly in domain compose YAML.
3. Avoid copying language assets into domain repos; always reference language layers via dependency metadata.
