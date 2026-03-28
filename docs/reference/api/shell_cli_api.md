# shell_cli API Reference

> **Source**: `src/thegent/shell_cli.py`

Shell environment management CLI commands.

---

## shell_benchmark

```python
shell_benchmark(iterations: int)
```

Benchmark shell startup time.

---

## shell_cache_stats

Show cache statistics (hit/miss rates, sizes).

---

## shell_circuit_breaker

```python
shell_circuit_breaker(reset: Any, list_all: bool)
```

Manage circuit breakers for error recovery.

---

## shell_clear_cache

Clear shell optimization cache (eval cache, tool cache, etc.).

---

## shell_doctor

```python
shell_doctor(fix: bool)
```

Diagnose shell environment issues.

---

## shell_doctor_alias

```python
shell_doctor_alias(fix: bool)
```

Alias for shell doctor.

---

## shell_jobs

Show background job status.

---

## shell_metrics

Show shell performance metrics and statistics.

---

## shell_optimize

Optimize shell configuration for performance.

---

## shell_platform

Show platform detection and compatibility information.

---

## shell_profile

```python
shell_profile(enable: bool, disable: bool)
```

Enable or disable shell startup profiling.

---

## shell_profile_alias

```python
shell_profile_alias(enable: bool, disable: bool)
```

Alias for shell profile.

---

## shell_reload

Reload shell configuration (sources .zshrc).

---

## shell_status

Show shell environment status and configuration.

---

## shell_status_alias

Alias for shell status.

---

