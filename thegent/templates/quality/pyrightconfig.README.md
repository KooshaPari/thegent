# Pyright/Pylance Configuration Template

This template provides optimal Pyright/Pylance configuration for Python projects with aggressive performance optimizations.

## Usage

Copy to project root:

```bash
cp thegent/templates/quality/pyrightconfig.json ./pyrightconfig.json
```

## Key Features

### Aggressive Exclusions
Prevents Pyright from indexing:
- Virtual environments (`.venv`, `venv`, `env`)
- Build artifacts (`dist`, `build`, `__pycache__`)
- Cache directories (`.pytest_cache`, `.mypy_cache`, `.ruff_cache`)
- Git worktrees (`.worktrees`)
- Node modules and dependencies
- IDE directories (`.vscode`, `.cursor`, `.idea`)

### Type Checking Mode
- **Basic mode** - Balance between performance and type safety
- Can be changed to `"off"` for fastest performance or `"strict"` for maximum type safety

### Execution Environments
- Separate environments for `src/` and `tests/`
- Tests can import from `src/` via `extraPaths`

## Performance Impact

- **50-80% faster** language server startup
- **Reduced memory usage** by excluding large dependency directories
- **Faster IntelliSense** by focusing on project code only

## Customization

### Adjust Python Version
Change `pythonVersion` to match your project:
```json
"pythonVersion": "3.11"
```

### Add Custom Exclusions
Add project-specific directories to `exclude`:
```json
"exclude": [
  "**/custom-build-dir",
  "**/generated-code"
]
```

### Change Type Checking Strictness
```json
"typeCheckingMode": "strict"  // or "off", "basic"
```

## Related Configuration

- `.vscode/settings.json` - VS Code/Cursor IDE settings (see `templates/ide/.vscode/settings.json`)
- `pyproject.toml` - Python project configuration (see `templates/python/pyproject.template.toml`)
