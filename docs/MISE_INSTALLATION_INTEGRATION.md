# mise Installation Integration - Current Behavior

## Status

- `--system-deps`, `--nix`, `--verify-mise`, and `--uninstall-mise-hooks` are not supported by the current `thegent` command parser in this tree.
- `src/thegent/install.py` still contains mise orchestration helpers (`install_mise`, `install_system_dependencies`),
  but these are now invoked through legacy/internal flows, not directly via the public command docs below.

## Current recommendation

- Keep `thegent install -t all` and `thegent setup` for project/thegent runtime bootstrap.
- Install and activate mise through your shell/toolchain workflow directly.

```bash
# Example
brew install mise
mise activate zsh  # or your preferred shell
```

## Source of truth for behavior

- For source parity, prefer command definitions in:
  - `src/thegent/cli/apps/main.py` (`thegent setup`)
  - `src/thegent/cli/apps/project.py` (`thegent install`)
  - `src/thegent/cli/commands/model_cmds.py` (`thegent setup` legacy helper path)
