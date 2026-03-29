# Zuban Type Checker Configuration

Zuban is a fast Python type checker used alongside `ty` for fast CI feedback.

## Usage

Zuban is configured via command-line flags (no config file support currently).

### Standard Configuration

```bash
zuban check src/ \
  --disable-error-code call-overload \
  --disable-error-code unreachable \
  --disable-error-code assignment \
  --disable-error-code var-annotated \
  --disable-error-code override \
  --disable-error-code return-value \
  --disable-error-code arg-type \
  --disable-error-code union-attr \
  --disable-error-code dict-item \
  --disable-error-code misc \
  --disable-error-code no-redef \
  --disable-error-code call-arg \
  --disable-error-code operator
```

## Integration

### Taskfile

```yaml
lint:type:
  desc: "Fast static type checking (ty + zuban)"
  cmds:
    - uv run ty check src/
    - uv run zuban check src/ --disable-error-code call-overload --disable-error-code unreachable --disable-error-code assignment --disable-error-code var-annotated --disable-error-code override --disable-error-code return-value --disable-error-code arg-type --disable-error-code union-attr --disable-error-code dict-item --disable-error-code misc --disable-error-code no-redef --disable-error-code call-arg --disable-error-code operator
```

### Pre-commit

Zuban is typically used in CI/linting tasks, not pre-commit (too slow for pre-commit hooks).

## Error Codes Disabled

The following error codes are disabled for faster feedback with fewer false positives:

- `call-overload` - Overload resolution issues
- `unreachable` - Unreachable code
- `assignment` - Assignment type mismatches
- `var-annotated` - Variable annotation issues
- `override` - Override decorator issues
- `return-value` - Return value type mismatches
- `arg-type` - Argument type mismatches
- `union-attr` - Union attribute access
- `dict-item` - Dictionary item type issues
- `misc` - Miscellaneous errors
- `no-redef` - Redefinition errors
- `call-arg` - Call argument issues
- `operator` - Operator overloading issues

## Customization

Adjust disabled error codes based on your project's needs. More strict checking = slower but more comprehensive.

## Related

- `ty` - Primary fast type checker
- `basedpyright` - Strict type checker (CI/commit)
- `mypy` - Additional strict checking
