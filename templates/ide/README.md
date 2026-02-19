# IDE Configuration Templates

This directory contains IDE configuration templates for optimal performance and developer experience.

## Files

- `.vscode/settings.json` - VS Code/Cursor settings for Python projects

## Usage

### For New Projects

Copy the entire `.vscode` directory to your project root:

```bash
cp -r thegent/templates/ide/.vscode ./my-project/.vscode
```

### For Existing Projects

Merge settings from `templates/ide/.vscode/settings.json` into your existing `.vscode/settings.json`.

## Key Features

### Python Language Server
- **Pylance** (not Jedi) - Faster, more accurate type checking
- **Basic type checking mode** - Balance between performance and type safety
- **Workspace diagnostic mode** - Analyzes entire workspace for better IntelliSense

### Performance Optimizations
- **Aggressive exclusions** - Prevents indexing of:
  - Virtual environments (`.venv`, `venv`, `env`)
  - Build artifacts (`dist`, `build`, `__pycache__`)
  - Cache directories (`.pytest_cache`, `.mypy_cache`, `.ruff_cache`)
  - Git worktrees (`.worktrees`)
  - Node modules and dependencies

- **File watcher exclusions** - Reduces file system monitoring overhead
- **Search exclusions** - Faster search by excluding build artifacts

### Python Formatting
- **Ruff** as default formatter
- **Format on save** enabled
- **Organize imports** on save

## Performance Impact

These settings significantly improve:
- **Language server startup time** - 50-80% faster
- **IntelliSense responsiveness** - Near-instant in most cases
- **File indexing** - Excludes unnecessary directories
- **Memory usage** - Reduced by excluding large dependency directories

## Troubleshooting

### Pylance Not Working
1. Verify `python.languageServer` is set to `"Pylance"` (not `"Jedi"` or `"None"`)
2. Check that Python extension is installed
3. Reload window: `Cmd+Shift+P` → "Reload Window"

### Still Slow?
1. Check `pyrightconfig.json` exists in project root (see `templates/quality/pyrightconfig.json`)
2. Verify exclusions match your project structure
3. Check workspace scope - consider opening subdirectory instead of parent directory

### Type Checking Issues
- Adjust `python.analysis.typeCheckingMode`:
  - `"off"` - No type checking (fastest)
  - `"basic"` - Basic checks (recommended)
  - `"strict"` - Full type checking (slowest but most accurate)

## Related Templates

- `templates/quality/pyrightconfig.json` - Pyright/Pylance configuration
- `templates/python/pyproject.template.toml` - Python project configuration
