# Ultra-Shim Fork Failure Fix: Root Cause Analysis & Solution

> **Status**: Critical Fix Plan | **Version**: 1.0 | **Date**: 2026-02-16
> **Purpose**: Fix fork exhaustion and permission errors in ultra-shim causing command failures

---

## Problem Summary

**Symptoms**:
- `find` commands failing with "fork: retry: Resource temporarily unavailable"
- `cat` commands failing with fork errors
- Permission denied errors when trying to execute files in `src/` as commands
- Commands taking 7+ seconds and exiting with code 1

**Root Causes**:
1. **Fork Exhaustion**: `runAndCache()` uses `exec.Command` which forks, hitting system resource limits
2. **Recursive Loops**: `tryIndex()` calls `grep` which may be intercepted by shim → fork fails → retries → exhausts resources
3. **Broken PATH Resolution**: Shell trying to execute files in `src/` as commands (PATH corruption)
4. **No Graceful Degradation**: Shim doesn't detect resource exhaustion and fall back to real binaries

---

## Root Cause Analysis

### 1. Fork Exhaustion in `runAndCache()`

**Current Code** (line 473-482):
```go
func runAndCache(path string, args []string, tool string, originalArgs []string) {
	cmd := exec.Command(path, args...)  // FORKS - can fail under resource pressure
	cmd.Env = os.Environ()
	output, err := cmd.CombinedOutput()
	if err == nil {
		saveCache(tool, originalArgs, output)
	}
	os.Stdout.Write(output)
	os.Exit(0)
}
```

**Problem**: When system is under load or has fork limits, `exec.Command` fails, but function doesn't handle it gracefully.

### 2. Recursive Interception in `tryIndex()`

**Current Code** (line 509):
```go
cmd := exec.Command("grep", "-E", grepPattern, indexPath)  // May be intercepted by shim!
```

**Problem**: `grep` command may be intercepted by ultra-shim, creating recursive loop.

### 3. PATH Corruption

**Current Behavior**:
- Shell's PATH includes project directory (`src/`)
- When resolving commands, it tries to execute Python files as commands
- Results in "permission denied" errors

**Problem**: `resolveReal()` doesn't properly filter out non-executable files from PATH.

---

## Immediate Fixes

### Fix 1: Add Fork Failure Detection to `runAndCache()`

**Change**: Modify `runAndCache()` to detect fork failures and fall back:

```go
func runAndCache(path string, args []string, tool string, originalArgs []string) {
	// Try fork first (for caching)
	cmd := exec.Command(path, args...)
	cmd.Env = os.Environ()
	output, err := cmd.CombinedOutput()

	if err != nil {
		// Check if it's a fork/resource error
		errStr := err.Error()
		if strings.Contains(errStr, "fork") ||
		   strings.Contains(errStr, "resource temporarily unavailable") ||
		   strings.Contains(errStr, "too many processes") {
			// Fork failed: fall back to direct exec (no fork, no caching)
			argv := append([]string{filepath.Base(path)}, args...)
			syscall.Exec(path, argv, os.Environ())
			os.Exit(1) // Should not reach here
		}
		// Other errors: write output and exit with error code
		os.Stdout.Write(output)
		if exitError, ok := err.(*exec.ExitError); ok {
			os.Exit(exitError.ExitCode())
		}
		os.Exit(1)
	}

	// Success: cache and output
	if len(output) > 0 {
		saveCache(tool, originalArgs, output)
	}
	os.Stdout.Write(output)
	os.Exit(0)
}
```

### Fix 2: Fix Recursive Interception in `tryIndex()`

**Change**: Use absolute path to real `grep`:

```go
func tryIndex(dir string, pattern string) bool {
	if os.Getenv("USE_INDEX") == "0" { return false }

	indexPath := getIndexFile()
	info, err := os.Stat(indexPath)
	if err != nil { return false }

	// TTL: 5 minutes for index
	if time.Since(info.ModTime()).Minutes() > 5 {
		return false
	}

	if pattern == "" { return false }

	// Normalize pattern for grep
	grepPattern := strings.ReplaceAll(pattern, "*", ".*")

	// Use absolute path to real grep (avoid shim interception)
	grepPath := resolveReal("grep", "")
	if grepPath == "" {
		grepPath = "/usr/bin/grep" // Fallback
	}

	var cmd *exec.Cmd
	if dir != "." {
		// Filter by directory
		cmd = exec.Command("sh", "-c", fmt.Sprintf("%s -E '%s' %s | %s '^%s'",
			grepPath, grepPattern, indexPath, grepPath, dir))
	} else {
		cmd = exec.Command(grepPath, "-E", grepPattern, indexPath)
	}

	output, err := cmd.CombinedOutput()
	if err == nil && len(output) > 0 {
		os.Stdout.Write(output)
		return true
	}
	return false
}
```

### Fix 3: Add Bypass Mechanism

**Change**: Add environment variable check at start of handlers:

```go
func handleFind(args []string, isAgent bool, self string) {
	// Check if shim should be bypassed
	if os.Getenv("BYPASS_ULTRA_SHIM") == "1" || os.Getenv("USE_FAST_FIND") == "0" {
		execute(resolveReal("find", self), args, self)
		return
	}

	// ... rest of handleFind()
}

func handleCat(args []string, self string) {
	// Check if shim should be bypassed
	if os.Getenv("BYPASS_ULTRA_SHIM") == "1" || os.Getenv("USE_FAST_CAT") == "0" {
		execute(resolveReal("cat", self), args, self)
		return
	}

	// ... rest of handleCat()
}
```

### Fix 4: Improve `resolveReal()` to Filter Non-Executables

**Change**: Check if file is actually executable:

```go
func resolveReal(name, self string) string {
	paths := []string{"/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"}
	for _, p := range paths {
		full := filepath.Join(p, name)
		info, err := os.Stat(full)
		if err != nil {
			continue
		}

		// Skip directories
		if info.IsDir() {
			continue
		}

		// Check if executable (not a Python file or other non-executable)
		mode := info.Mode()
		if !mode.IsRegular() {
			continue
		}

		// Check if executable bit is set (or if it's a script with shebang)
		if mode&0111 == 0 {
			// Might be a script - check first line for shebang
			if !hasShebang(full) {
				continue
			}
		}

		// Make sure it's not the shim itself
		if isSelfBinary(full, self) {
			continue
		}

		return full
	}
	return ""
}

func hasShebang(path string) bool {
	f, err := os.Open(path)
	if err != nil {
		return false
	}
	defer f.Close()

	var firstLine [2]byte
	if n, _ := f.Read(firstLine[:]); n == 2 && firstLine[0] == '#' && firstLine[1] == '!' {
		return true
	}
	return false
}
```

---

## Long-Term Fixes

### Fix 5: Implement Circuit Breaker Pattern

**Change**: Add circuit breaker to detect and prevent fork failures:

```go
var (
	forkFailureCount int
	lastForkFailure  time.Time
	circuitOpen      bool
	circuitMutex     sync.Mutex
)

func executeWithCircuitBreaker(path string, args []string, self string) {
	circuitMutex.Lock()

	// Check circuit breaker
	if circuitOpen {
		if time.Since(lastForkFailure) > 30*time.Second {
			// Reset after 30 seconds
			circuitOpen = false
			forkFailureCount = 0
		} else {
			// Circuit open: bypass shim, use direct exec
			circuitMutex.Unlock()
			argv := append([]string{filepath.Base(path)}, args...)
			syscall.Exec(path, argv, os.Environ())
			os.Exit(1)
		}
	}

	circuitMutex.Unlock()

	// Try fork
	cmd := exec.Command(path, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	if err != nil {
		errStr := err.Error()
		if strings.Contains(errStr, "fork") ||
		   strings.Contains(errStr, "resource temporarily unavailable") {

			circuitMutex.Lock()
			forkFailureCount++
			lastForkFailure = time.Now()

			if forkFailureCount >= 3 {
				circuitOpen = true
				os.Setenv("ULTRA_SHIM_FORK_FAILURES", strconv.Itoa(forkFailureCount))
			}
			circuitMutex.Unlock()

			// Fall back to direct exec
			argv := append([]string{filepath.Base(path)}, args...)
			syscall.Exec(path, argv, os.Environ())
			os.Exit(1)
		}

		// Other errors
		if exitError, ok := err.(*exec.ExitError); ok {
			os.Exit(exitError.ExitCode())
		}
		os.Exit(1)
	}

	// Success: reset counter
	circuitMutex.Lock()
	if forkFailureCount > 0 {
		forkFailureCount = 0
	}
	circuitMutex.Unlock()
}
```

### Fix 6: Reduce Fork Overhead for Simple Cases

**Change**: Use `syscall.Exec` for simple cases (no fork needed):

```go
func execute(path string, args []string, self string) {
	if path == "" || isSelfBinary(path, self) {
		os.Exit(127)
	}

	// For simple commands without caching/indexing, use Exec (no fork)
	// This is faster and doesn't consume fork resources
	argv := append([]string{filepath.Base(path)}, args...)
	syscall.Exec(path, argv, os.Environ())
	os.Exit(1) // Should not reach here if exec succeeds
}
```

---

## Implementation Plan

### Phase 1: Immediate Fixes (Today)

1. ✅ **Add fork failure detection** to `runAndCache()`
2. ✅ **Fix recursive interception** in `tryIndex()`
3. ✅ **Add bypass mechanism** via environment variables
4. ✅ **Improve `resolveReal()`** to filter non-executables

### Phase 2: Circuit Breaker (Tomorrow)

1. **Implement circuit breaker pattern**
2. **Add resource limit detection**
3. **Add monitoring/logging**
4. **Test under resource pressure**

### Phase 3: Optimization (Day 3)

1. **Reduce fork overhead** (use Exec for simple cases)
2. **Fix shell PATH corruption** (update `hooks/lib/common.sh`)
3. **Performance testing**
4. **Documentation**

---

## Testing

### Test Cases

1. **Fork Exhaustion**:
   ```bash
   # Simulate fork exhaustion
   ulimit -u 10
   find ~/.codex -type f
   # Should fall back to direct exec, not fail
   ```

2. **PATH Corruption**:
   ```bash
   # Test PATH resolution
   PATH="$PWD/src:$PATH" find --version
   # Should find real find, not try to execute Python files
   ```

3. **Circuit Breaker**:
   ```bash
   # Trigger multiple fork failures
   for i in {1..5}; do find ~/.codex -type f; done
   # Should open circuit after 3 failures
   ```

---

## Quick Fix for Users

**Immediate workaround**:
```bash
# Bypass shim temporarily
export BYPASS_ULTRA_SHIM=1
export USE_FAST_FIND=0
export USE_FAST_CAT=0

# Or use real binaries directly
/usr/bin/find ~/.codex -type f
```

---

## Conclusion

The root cause is fork exhaustion in `runAndCache()` combined with recursive interception and PATH corruption. The fixes include:

1. **Immediate**: Fork failure detection + fallback to Exec
2. **Short-term**: Circuit breaker pattern
3. **Long-term**: Reduce fork overhead, fix PATH resolution

**Priority**: **P0** (Critical - blocking all commands)

---

**Document Status**: Complete | **Last Updated**: 2026-02-16


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
