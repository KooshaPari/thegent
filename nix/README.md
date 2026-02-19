# thegent Nix Integration

## Build the package

```bash
# Ensure nix/ is tracked by Git (required for flake evaluation)
git add nix/

# Build
nix build .#thegent
```

If you see "Path 'nix/...' is not tracked by Git", run `git add nix/` and commit (or use a worktree with tracked files).

## Flake outputs

| Output | Description |
|--------|-------------|
| `packages.${system}.thegent` | thegent CLI |
| `homeManagerModules.thegent` | home-manager module |
| `devenvModules.thegent` | devenv module |
| `nixDarwinModules.thegent` | nix-darwin module (MCP + lock-cleanup) |

## Package dependencies

The Nix package uses `buildPythonApplication` with dependencies from nixpkgs. Build requires `hatch-vcs` for dynamic version from git. Some packages (e.g. `granian`, `fastmcp`, `hatch-vcs`) may not yet be in nixpkgs. If the build fails on missing dependencies:

- Use `uv tool install thegent` or `pip install thegent` instead
- Or add the missing packages to nixpkgs and contribute upstream
- For `hatch-vcs` specifically: the pyproject uses dynamic version; if unavailable, you can patch to static version
