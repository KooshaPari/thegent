# Archived Deprecated Lib Stubs

These directories were archived on 2026-03-27 as part of `chore/archive-deprecated-lib-stubs`.

All entries below contained only LICENSE and/or README files — no implementation code.

| Directory            | Original Path         | Reason                                                  |
|----------------------|-----------------------|---------------------------------------------------------|
| `hexagon-rs/`        | `libs/hexagon-rs/`    | Stub. Canonical: `libs/hexagonal-rs/`                   |
| `hexagon-python/`    | `libs/hexagon-python/`| Stub. Canonical: `libs/hexagonal-py/`                   |
| `hexagon-ts/`        | `libs/hexagon-ts/`    | Stub. Canonical: `libs/hexagonal-ts/`                   |
| `hexagon-java/`      | `libs/hexagon-java/`  | Stub. No canonical Java hex lib currently in scope.     |
| `hexagon-rust/`      | `libs/hexagon-rust/`  | Stub. Canonical: `libs/hexagonal-rs/`                   |
| `hexagon-elixir/`    | `libs/hexagon-elixir/`| Stub. No canonical Elixir hex lib currently in scope.   |
| `hexkit-root-stub/`  | `hexkit/` (repo root) | Root-level stub (CLAUDE.md only). Canonical: `libs/hexkit/` |

## Recovery

If any archived directory needs to be restored, use:

```bash
git show <commit-before-archive>:libs/<dirname>
```

Or copy directly from `.archive/deprecated-libs/<dirname>` back to `libs/`.
