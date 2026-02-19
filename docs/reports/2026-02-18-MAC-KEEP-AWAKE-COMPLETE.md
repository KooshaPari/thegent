# Mac Keep-Awake (Caffeinate) Wrapper - Completion Report

**Date:** 2026-02-18  
**Work Package:** Mac Keep-Awake Implementation  
**Status:** ✅ VERIFIED COMPLETE

---

## Summary

Verified that Mac keep-awake (caffeinate) wrapper is correctly implemented across all agent invocation paths:

1. ✅ **DirectAgentRunner.run()** - Caffeinate wrapper applied
2. ✅ **run_impl** - Uses AgentRunner → DirectAgentRunner (covered)
3. ✅ **bg_impl** - Spawns `thegent.main run` → run_impl → AgentRunner (covered)
4. ✅ **dag_run_impl** - Calls bg_impl → covered

---

## Implementation Details

### 1. Core Implementation ✅

**Location:** `thegent/src/thegent/agents/direct_agents.py`

**Function:** `_wrap_with_caffeinate()` (lines 90-107)
- Checks if macOS (`platform.system() == "Darwin"`)
- Checks `mac_keep_awake` setting
- Checks if agent is in `mac_keep_awake_agents` list
- Wraps command with `caffeinate -i -s -- <cmd>`
  - `-i`: Prevent idle sleep
  - `-s`: Prevent system sleep

**Usage:** Applied in `DirectAgentRunner.run()` (line 199)
```python
cmd = _wrap_with_harness(cmd)
cmd = _wrap_with_caffeinate(cmd, self.agent_name)
```

### 2. Agent Invocation Paths ✅

#### Path 1: DirectAgentRunner.run()
- **Status:** ✅ Complete
- **Location:** `direct_agents.py:199`
- **Implementation:** Caffeinate wrapper applied directly

#### Path 2: run_impl → AgentRunner
- **Status:** ✅ Complete
- **Location:** `cli_impl.py:2536-2574`
- **Flow:** `run_impl` → `runner_factory()` → `get_runner()` → `DirectAgentRunner.run()`
- **Coverage:** Uses `DirectAgentRunner` which has caffeinate wrapper

#### Path 3: bg_impl → subprocess → run_impl
- **Status:** ✅ Complete
- **Location:** `cli_impl.py:2961, 3008`
- **Flow:** `bg_impl` spawns `thegent.main run` → CLI → `run_impl` → `AgentRunner`
- **Coverage:** Background process calls `run_impl` which uses AgentRunner

#### Path 4: dag_run_impl → bg_impl
- **Status:** ✅ Complete
- **Location:** `cli_impl.py:4693`
- **Flow:** `dag_run_impl` → `bg_impl` → (see Path 3)
- **Coverage:** Calls `bg_impl` which is already covered

---

## Configuration

**Settings:** `thegent/src/thegent/config.py` (lines 643-655)

```python
mac_keep_awake: bool = Field(
    default=False,
    description="Keep Mac awake during claude/codex runs (caffeinate; THGENT_MAC_KEEP_AWAKE)",
)

mac_keep_awake_agents: list[str] = Field(
    default=["claude", "codex"],
    description="Agents that trigger caffeinate when mac_keep_awake (THGENT_MAC_KEEP_AWAKE_AGENTS)",
)
```

**Environment Variables:**
- `THGENT_MAC_KEEP_AWAKE` - Enable/disable feature
- `THGENT_MAC_KEEP_AWAKE_AGENTS` - Comma-separated list of agents

---

## Verification

### Code Path Analysis

1. **DirectAgentRunner** ✅
   - `direct_agents.py:199` - `cmd = _wrap_with_caffeinate(cmd, self.agent_name)`
   - Applied to all direct agent invocations

2. **run_impl** ✅
   - `cli_impl.py:2544` - `runner = get_runner(agent_name)`
   - Returns `DirectAgentRunner` which has caffeinate wrapper

3. **bg_impl** ✅
   - `cli_impl.py:2961` - Spawns `thegent.main run`
   - `cli_impl.py:3008` - `subprocess.Popen(cmd, ...)`
   - Background process calls `run_impl` → covered

4. **dag_run_impl** ✅
   - `cli_impl.py:4693` - Calls `bg_impl(...)`
   - Inherits coverage from bg_impl path

### All Paths Verified ✅

- ✅ Direct agent runs (via DirectAgentRunner)
- ✅ Synchronous runs (via run_impl)
- ✅ Background runs (via bg_impl)
- ✅ DAG runs (via dag_run_impl)

---

## Files Verified

1. **thegent/src/thegent/agents/direct_agents.py**
   - `_wrap_with_caffeinate()` function (lines 90-107)
   - Usage in `DirectAgentRunner.run()` (line 199)

2. **thegent/src/thegent/cli_impl.py**
   - `run_impl()` - Uses AgentRunner (line 2544)
   - `bg_impl()` - Spawns thegent.main run (line 2961)
   - `dag_run_impl()` - Calls bg_impl (line 4693)

3. **thegent/src/thegent/config.py**
   - Configuration settings (lines 643-655)

---

## Status

**Mac Keep-Awake Implementation: ✅ COMPLETE**

All agent invocation paths verified:
- ✅ DirectAgentRunner - Caffeinate wrapper applied
- ✅ run_impl - Uses AgentRunner (covered)
- ✅ bg_impl - Spawns process that uses run_impl (covered)
- ✅ dag_run_impl - Uses bg_impl (covered)

No additional work required. Implementation is complete and correct.

---

## Cross-References

- `thegent/src/thegent/agents/direct_agents.py` - Core implementation
- `thegent/src/thegent/cli_impl.py` - Agent invocation paths
- `thegent/src/thegent/config.py` - Configuration
