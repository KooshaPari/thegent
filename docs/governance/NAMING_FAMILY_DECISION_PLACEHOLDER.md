# Naming family for neutral packages — decision placeholder

**Task:** Item 3 — confirm standard prefix for market-neutral extracted libraries (`forge-*`, `port-*`, `kit-*`, or other).

## Status

**OPEN** — requires org owner confirmation (trademark, npm/crates.io availability).

## Candidates

| Family | Example | Notes |
|--------|---------|--------|
| `kit-*` | `hexkit-go` | Short, generic |
| `port-*` | `port-auth-ts` | Emphasizes hexagonal ports |
| `forge-*` | **Avoid collision** with **Forge CLI** (`forge` binary) — use only if explicitly disambiguated |

## Recommendation

- Use **`kit-*` or `port-*`** for **libraries**; reserve **Forge** for the **headless CLI** product name to avoid confusion with `forge` the binary.

## Next step

- Replace this file with ADR-00xx once decided; update `POLYREPO_PACKAGE_NAMING_AND_PRODUCTIZATION.md`.
