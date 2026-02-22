# Cross-Platform Multi-Tenant Desktop Automation Implementation Plan

**Purpose:** Phased WBS for implementing Windows/Linux/macOS support, agent-user isolation, multi-tenant coordination, and desktop automation.

**Date:** 2026-02-16
**Status:** Planning
**Related:** CROSS_PLATFORM_MULTI_TENANT_DESKTOP_AUTOMATION_RESEARCH.md

---

## Phased Work Breakdown Structure

### Phase 1: User Isolation Foundation
**Goal:** Implement hybrid user model (sub-user + optional OS users)
**Duration:** 2 weeks
**Effort:** 15-25 tool calls, 2-3 parallel subagents, ~8-12 min

#### P1.1: SystemUser Abstraction
- [ ] Create `src/thegent/infra/user_isolation.py`
- [ ] Implement `SystemUser` base class
  - [ ] `uid`, `gid`, `username`, `home`, `shell`, `groups`
  - [ ] `from_current()` classmethod (detect current user)
  - [ ] `to_dict()` / `from_dict()` serialization
- [ ] Implement `AgentUser(SystemUser)` subclass
  - [ ] `agent_id`, `workspace`, `capabilities` (set)
- [ ] Add platform detection utilities
  - [ ] `detect_platform()` → "darwin" | "linux" | "windows"
  - [ ] `get_current_user()` → SystemUser instance
- [ ] Unit tests: `tests/test_user_isolation.py`
  - [ ] Test SystemUser creation
  - [ ] Test AgentUser capabilities
  - [ ] Test platform detection

**Depends on:** None
**Deliverable:** `src/thegent/infra/user_isolation.py` + tests

#### P1.2: OS User Creation (macOS/Linux)
- [ ] Create `src/thegent/infra/os_user_manager.py`
- [ ] Implement `create_os_user()` for macOS/Linux
  - [ ] macOS: `dscl` commands or `useradd` wrapper
  - [ ] Linux: `useradd -r -s /bin/false`
  - [ ] Create home directory: `/var/lib/thegent/agents/{username}`
  - [ ] Set permissions: `chown {username}:{username}`
- [ ] Implement `delete_os_user()` for cleanup
- [ ] Add error handling (permission denied, user exists)
- [ ] Unit tests: `tests/test_os_user_manager.py`
  - [ ] Test user creation (requires root, skip in CI)
  - [ ] Test user deletion
  - [ ] Test error cases

**Depends on:** P1.1
**Deliverable:** `src/thegent/infra/os_user_manager.py` + tests

#### P1.3: OS User Creation (Windows)
- [ ] Extend `os_user_manager.py` for Windows
- [ ] Implement `create_os_user_windows()`
  - [ ] Use `New-LocalUser` PowerShell cmdlet
  - [ ] Create home: `C:\ProgramData\thegent\agents\{username}`
  - [ ] Set permissions via `icacls`
- [ ] Implement `delete_os_user_windows()`
  - [ ] Use `Remove-LocalUser` PowerShell cmdlet
- [ ] Add Windows-specific error handling
- [ ] Unit tests: `tests/test_os_user_manager_windows.py`
  - [ ] Test user creation (requires admin, skip in CI)
  - [ ] Test user deletion

**Depends on:** P1.2
**Deliverable:** Windows support in `os_user_manager.py` + tests

#### P1.4: AgentUserPool
- [ ] Create `src/thegent/infra/user_pool.py`
- [ ] Implement `AgentUserPool` class
  - [ ] `__init__(pool_size: int, base_path: Path)`
  - [ ] `acquire(agent_id: str) -> SystemUser`
  - [ ] `release(user: SystemUser)`
  - [ ] `_create_pool()` — pre-create OS users
  - [ ] Round-robin or least-used assignment
- [ ] Add pool overflow handling (create on-demand)
- [ ] Add pool cleanup on shutdown
- [ ] Unit tests: `tests/test_user_pool.py`
  - [ ] Test pool acquisition/release
  - [ ] Test overflow handling
  - [ ] Test cleanup

**Depends on:** P1.2, P1.3
**Deliverable:** `src/thegent/infra/user_pool.py` + tests

#### P1.5: AgentRunner Integration
- [ ] Update `src/thegent/agents/base.py`
  - [ ] Add `isolation_mode: Literal["subuser", "osuser", "docker"]` to `AgentRunner`
- [ ] Update `DirectAgentRunner.run()`
  - [ ] Check `isolation_mode`
  - [ ] If `osuser`: acquire user from pool, run as that user
  - [ ] If `subuser`: use current user, create `AgentUser` wrapper
  - [ ] If `docker`: delegate to Docker runner (future)
- [ ] Add `_run_as_user()` helper method
  - [ ] macOS/Linux: `subprocess.run(..., user=username)`
  - [ ] Windows: `subprocess.run(..., runas=username)` or `runas.exe`
- [ ] Update `CodexProxyRunner` similarly
- [ ] Integration tests: `tests/test_agent_runner_isolation.py`
  - [ ] Test subuser mode
  - [ ] Test osuser mode (requires root/admin, skip in CI)
  - [ ] Test user switching

**Depends on:** P1.1, P1.4
**Deliverable:** Updated `AgentRunner` + tests

#### P1.6: Configuration
- [ ] Add to `src/thegent/config.py`:
  ```python
  isolation_mode: str = "subuser"
  osuser_pool_size: int = 10
  osuser_base_path: Path = Path("/var/lib/thegent/agents")
  ```
- [ ] Add to `~/.thegent/config.yaml`:
  ```yaml
  isolation:
    mode: "subuser"
    osuser_pool_size: 10
    osuser_base_path: "/var/lib/thegent/agents"
  shell:
    agent_shell: "bash"  # bash | pwsh | wsl-bash
  ```
- [ ] Add CLI flag: `thegent run --isolation-mode {subuser|osuser|docker}`
- [ ] Environment variable: `THGENT_ISOLATION_MODE=osuser`
- [ ] Documentation: `docs/guides/USER_ISOLATION.md`

**Depends on:** P1.5
**Deliverable:** Configuration + docs

#### P1.7: Shell Strategy (POSIX + pwsh)
- [ ] Create `src/thegent/infra/shell_detection.py`
  - [ ] `get_preferred_shell(platform, context)` → "bash" | "pwsh" | "wsl-bash"
  - [ ] Contexts: `hooks`, `agent`, `os_admin`, `desktop`
  - [ ] Windows: prefer WSL2 bash for hooks/agent if available; pwsh for os_admin/desktop
- [ ] Add `THGENT_AGENT_SHELL` config (bash | pwsh | wsl-bash) to config
- [ ] Create `docs/reference/POSIX_PWSH_SHELL_STRATEGY.md` (shell selection matrix, config)
- [ ] Unit tests: `tests/test_shell_detection.py`

**Depends on:** P1.1
**Deliverable:** Shell detection + docs
**Reference:** [CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md](../research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md) §2

---

### Phase 2: Multi-Tenant Coordination
**Goal:** Add conflict detection and resolution
**Duration:** 2 weeks
**Effort:** 20-30 tool calls, 3-4 parallel subagents, ~12-18 min

#### P2.1: Tenant-Aware Edit Lease Manager
- [ ] Update `src/thegent/orchestration/edit_lease.py` (existing)
- [ ] Add `tenant_id: str` field to `EditLease`
  - [ ] Format: `"user"` or `"agent-{id}"`
- [ ] Update `acquire()` to check tenant conflicts
  - [ ] Read leases: multiple tenants OK
  - [ ] Write leases: only one tenant
  - [ ] User can break agent leases (priority)
- [ ] Add `release_by_tenant(tenant_id: str)` for cleanup
- [ ] Update lease registry to track tenants
- [ ] Unit tests: `tests/test_tenant_aware_lease.py`
  - [ ] Test user priority
  - [ ] Test agent-agent conflicts
  - [ ] Test multi-reader

**Depends on:** None (extends existing)
**Deliverable:** Updated `edit_lease.py` + tests

#### P2.2: User Activity Detection
- [ ] Create `src/thegent/infra/user_activity.py`
- [ ] Implement `UserActivityDetector` abstract base
- [ ] Implement `macOSUserActivityDetector`
  - [ ] Use `CGEventSourceSecondsSinceLastEventType()` (CoreGraphics)
  - [ ] Check keyboard, mouse, tablet events
- [ ] Implement `LinuxUserActivityDetector`
  - [ ] X11: `XScreenSaverQueryInfo()` (if X11)
  - [ ] systemd: `loginctl show-user {username}` (if systemd)
  - [ ] Fallback: parse `/proc/{pid}/stat` for last CPU time
- [ ] Implement `WindowsUserActivityDetector`
  - [ ] Use `GetLastInputInfo()` (User32.dll via ctypes)
- [ ] Add `is_user_active(threshold_seconds: float) -> bool`
- [ ] Unit tests: `tests/test_user_activity.py`
  - [ ] Mock platform APIs
  - [ ] Test threshold logic

**Depends on:** None
**Deliverable:** `src/thegent/infra/user_activity.py` + tests

#### P2.3: Desktop Automation Coordinator
- [ ] Create `src/thegent/infra/desktop_coordinator.py`
- [ ] Implement `DesktopAutomationCoordinator`
  - [ ] `_active_automation: Optional[str]` (agent_id)
  - [ ] `_lock: threading.Lock`
  - [ ] `request_automation(agent_id: str) -> bool`
    - [ ] Check user activity (via `UserActivityDetector`)
    - [ ] Check existing automation lock
    - [ ] Acquire lock if available
  - [ ] `release_automation(agent_id: str)`
  - [ ] `wait_for_user_idle(idle_seconds: float) -> bool`
- [ ] Add timeout handling (auto-release after N seconds)
- [ ] Unit tests: `tests/test_desktop_coordinator.py`
  - [ ] Test user activity blocking
  - [ ] Test lock acquisition/release
  - [ ] Test timeout

**Depends on:** P2.2
**Deliverable:** `src/thegent/infra/desktop_coordinator.py` + tests

#### P2.4: Tenant-Aware Concurrency Controller
- [ ] Update `src/thegent/orchestration/concurrency_controller.py` (existing)
- [ ] Add tenant-aware limits:
  ```python
  max_user_processes: int = 5
  max_agent_processes: int = 10
  max_total_processes: int = 15
  ```
- [ ] Update `acquire()` to check tenant-specific limits
  - [ ] Count processes per tenant
  - [ ] Check tenant limit + total limit
- [ ] Add `_count_processes(tenant_pattern: str) -> int`
  - [ ] Parse process metadata (owner, agent_id)
- [ ] Unit tests: `tests/test_tenant_concurrency.py`
  - [ ] Test user limit enforcement
  - [ ] Test agent limit enforcement
  - [ ] Test total limit enforcement

**Depends on:** None (extends existing)
**Deliverable:** Updated `concurrency_controller.py` + tests

#### P2.5: Conflict Resolver
- [ ] Create `src/thegent/infra/conflict_resolver.py`
- [ ] Implement `ConflictResolver` class
  - [ ] `resolve_file_conflict(tenant_a: str, tenant_b: str, file: Path) -> str`
    - [ ] Policy: user priority → return "user"
    - [ ] Policy: FIFO → return first tenant
  - [ ] `resolve_resource_conflict(...) -> str`
  - [ ] `resolve_automation_conflict(...) -> str`
- [ ] Add conflict event logging
  - [ ] Log to `~/.thegent/logs/conflicts.jsonl`
- [ ] Add conflict metrics (count by type)
- [ ] Unit tests: `tests/test_conflict_resolver.py`
  - [ ] Test user priority policy
  - [ ] Test FIFO policy
  - [ ] Test logging

**Depends on:** P2.1, P2.3
**Deliverable:** `src/thegent/infra/conflict_resolver.py` + tests

#### P2.6: Configuration & Integration
- [ ] Add to config:
  ```yaml
  multi_tenant:
    user_priority: true
    conflict_resolution: "user_priority"
    user_idle_threshold_seconds: 5.0
    max_user_processes: 5
    max_agent_processes: 10
    max_total_processes: 15
  ```
- [ ] Wire coordinators into `AgentRunner`
  - [ ] Check user activity before automation
  - [ ] Acquire automation lock
  - [ ] Use tenant-aware leases
- [ ] Add CLI flags: `--max-user-processes`, `--max-agent-processes`
- [ ] Documentation: `docs/guides/MULTI_TENANT_COORDINATION.md`

**Depends on:** P2.1-P2.5
**Deliverable:** Configuration + integration + docs

#### P2.7: Hook Dispatcher Shell (Windows)
- [ ] Update hook dispatcher to use `get_preferred_shell()` on Windows
- [ ] Invoke hooks via `bash -c` or `wsl bash -c` when WSL2 available
- [ ] Add `hooks/lib/pwsh_adapters.ps1` for Windows-native hook logic (optional)
- [ ] Document: hooks call `pwsh -File` for Windows-specific blocks when needed

**Depends on:** P1.7
**Deliverable:** Hook dispatcher uses shell detection on Windows
**Reference:** [POSIX_PWSH_SHELL_STRATEGY.md](../reference/POSIX_PWSH_SHELL_STRATEGY.md)

---

### Phase 3: Desktop Automation Primitives
**Goal:** Implement platform-specific desktop automation
**Duration:** 3 weeks
**Effort:** 30-45 tool calls, 4-5 parallel subagents, ~18-25 min

#### P3.1: Desktop Automation Abstraction
- [ ] Create `src/thegent/infra/desktop_automation/`
- [ ] Create `base.py` with `DesktopAutomationProvider` abstract class
  - [ ] `click(element: UIElement) -> bool`
  - [ ] `type_text(element: UIElement, text: str) -> bool`
  - [ ] `find_element(selector: str) -> Optional[UIElement]`
  - [ ] `screenshot(region: Optional[dict] = None) -> bytes`
  - [ ] `wait_for_idle(seconds: float) -> bool`
- [ ] Create `UIElement` dataclass
  - [ ] `selector: str`, `name: str`, `role: str`, `bounds: dict`
- [ ] Create factory: `get_provider() -> DesktopAutomationProvider`
  - [ ] Auto-detect platform, return appropriate provider
- [ ] Unit tests: `tests/test_desktop_automation_base.py`
  - [ ] Test abstract interface
  - [ ] Test factory

**Depends on:** None
**Deliverable:** `src/thegent/infra/desktop_automation/base.py` + tests

#### P3.2: macOS Provider (AppleScript)
- [ ] Create `src/thegent/infra/desktop_automation/macos.py`
- [ ] Implement `macOSAutomationProvider(DesktopAutomationProvider)`
- [ ] Implement `click()` via AppleScript
  - [ ] `tell application "System Events" to click {element}`
- [ ] Implement `type_text()` via AppleScript
  - [ ] `tell application "System Events" to keystroke "{text}"`
- [ ] Implement `find_element()` via AppleScript
  - [ ] `tell application "System Events" to get {selector}`
- [ ] Implement `screenshot()` via `screencapture` command
- [ ] Add error handling (permission denied, element not found)
- [ ] Add dependency: `py-applescript` or subprocess wrapper
- [ ] Unit tests: `tests/test_macos_automation.py`
  - [ ] Mock AppleScript execution
  - [ ] Test error cases

**Depends on:** P3.1
**Deliverable:** `src/thegent/infra/desktop_automation/macos.py` + tests

#### P3.3: Windows Provider (UI Automation)
- [ ] Create `src/thegent/infra/desktop_automation/windows.py`
- [ ] Implement `WindowsAutomationProvider(DesktopAutomationProvider)`
- [ ] Use `pywinauto` or `uiautomation` library
- [ ] Implement `click()` via UIA
  - [ ] `element.click()` or `element.invoke()`
- [ ] Implement `type_text()` via UIA
  - [ ] `element.type_keys(text)`
- [ ] Implement `find_element()` via UIA
  - [ ] `Application().window(title="...").control(...)`
- [ ] Implement `screenshot()` via `PIL.ImageGrab` or `mss`
- [ ] Add error handling
- [ ] Add dependency: `pywinauto` or `uiautomation`
- [ ] Unit tests: `tests/test_windows_automation.py`
  - [ ] Mock UIA elements
  - [ ] Test error cases

**Depends on:** P3.1
**Deliverable:** `src/thegent/infra/desktop_automation/windows.py` + tests

#### P3.4: Linux Provider (AT-SPI)
- [ ] Create `src/thegent/infra/desktop_automation/linux.py`
- [ ] Implement `LinuxAutomationProvider(DesktopAutomationProvider)`
- [ ] Use `pyatspi` or `dogtail` library
- [ ] Implement `click()` via AT-SPI
  - [ ] `element.doAction(0)` (action 0 = click)
- [ ] Implement `type_text()` via AT-SPI
  - [ ] `element.setText(text)` or keyboard input
- [ ] Implement `find_element()` via AT-SPI
  - [ ] Traverse accessibility tree, match by name/role
- [ ] Implement `screenshot()` via `mss` or `PIL.ImageGrab`
- [ ] Add error handling
- [ ] Add dependency: `pyatspi` or `dogtail`
- [ ] Unit tests: `tests/test_linux_automation.py`
  - [ ] Mock AT-SPI elements
  - [ ] Test error cases

**Depends on:** P3.1
**Deliverable:** `src/thegent/infra/desktop_automation/linux.py` + tests

#### P3.5: Cross-Platform Testing
- [ ] Create integration tests: `tests/test_desktop_automation_integration.py`
- [ ] Test on macOS (requires Accessibility permission)
- [ ] Test on Linux (requires AT-SPI)
- [ ] Test on Windows (requires UIA Access)
- [ ] Test error handling (permission denied, element not found)
- [ ] Test performance (click latency, screenshot speed)
- [ ] Add CI/CD setup (skip on platforms without permissions)

**Depends on:** P3.2, P3.3, P3.4
**Deliverable:** Integration tests + CI setup

#### P3.6: Documentation & Examples
- [ ] Create `docs/guides/DESKTOP_AUTOMATION.md`
  - [ ] Platform setup (permissions)
  - [ ] Usage examples
  - [ ] Troubleshooting
- [ ] Create example workflows:
  - [ ] `examples/desktop_automation/click_button.py`
  - [ ] `examples/desktop_automation/fill_form.py`
- [ ] Add to `pyproject.toml` dependencies:
  - [ ] `py-applescript` (macOS, optional)
  - [ ] `pywinauto` (Windows, optional)
  - [ ] `pyatspi` (Linux, optional)

**Depends on:** P3.1-P3.5
**Deliverable:** Documentation + examples

---

### Phase 4: MCP Integration
**Goal:** Expose desktop automation via MCP
**Duration:** 1 week
**Effort:** 15-20 tool calls, 2-3 parallel subagents, ~8-12 min

#### P4.1: MCP Tools Registration
- [ ] Update `src/thegent/mcp_server.py`
- [ ] Register desktop automation tools:
  ```python
  @mcp.tool()
  def desktop_automation_click(selector: str, wait_timeout: float = 5.0) -> dict:
      """Click a UI element."""
      provider = get_provider()
      element = provider.find_element(selector, timeout=wait_timeout)
      if not element:
          return {"success": False, "error": "Element not found"}
      success = provider.click(element)
      return {"success": success}

  @mcp.tool()
  def desktop_automation_type(selector: str, text: str, wait_timeout: float = 5.0) -> dict:
      """Type text into a UI element."""
      # Similar implementation

  @mcp.tool()
  def desktop_automation_find(selector: str, timeout: float = 5.0) -> dict:
      """Find UI element by selector."""
      # Similar implementation

  @mcp.tool()
  def desktop_automation_screenshot(region: Optional[dict] = None) -> dict:
      """Take screenshot."""
      # Similar implementation

  @mcp.tool()
  def desktop_automation_wait_for_user_idle(idle_seconds: float = 5.0) -> dict:
      """Wait until user is idle."""
      # Similar implementation
  ```
- [ ] Add coordination hooks (check user activity, acquire lock)
- [ ] Add error handling and logging
- [ ] Unit tests: `tests/test_mcp_desktop_automation.py`

**Depends on:** P3.1-P3.4, P2.3
**Deliverable:** MCP tools + tests

#### P4.2: MCP Resources
- [ ] Add MCP resource: `thegent://desktop-automation/status`
  - [ ] Returns: `{"active": bool, "agent_id": str | None, "user_active": bool}`
- [ ] Add MCP resource: `thegent://desktop-automation/permissions`
  - [ ] Returns: `{"macos_accessibility": bool, "windows_uia": bool, "linux_atspi": bool}`
- [ ] Update MCP server to serve these resources
- [ ] Unit tests: `tests/test_mcp_desktop_resources.py`

**Depends on:** P4.1
**Deliverable:** MCP resources + tests

#### P4.3: Example Workflows
- [ ] Create `examples/mcp_desktop_automation/`
- [ ] Example: Click button workflow
- [ ] Example: Fill form workflow
- [ ] Example: Multi-step automation workflow
- [ ] Documentation: `docs/guides/MCP_DESKTOP_AUTOMATION.md`

**Depends on:** P4.1, P4.2
**Deliverable:** Examples + docs

---

### Phase 5: Testing & Polish
**Goal:** Cross-platform testing and documentation
**Duration:** 1 week
**Effort:** 20-30 tool calls, 3-4 parallel subagents, ~12-18 min

#### P5.1: Cross-Platform Testing
- [ ] Test user isolation on macOS, Linux, Windows
- [ ] Test multi-tenant coordination scenarios
- [ ] Test desktop automation on all platforms
- [ ] Test MCP integration end-to-end
- [ ] Performance benchmarking
- [ ] Fix platform-specific bugs

**Depends on:** P1-P4
**Deliverable:** Test results + bug fixes

#### P5.2: Documentation Updates
- [ ] Update `README.md` with cross-platform support
- [ ] Create migration guide: `docs/guides/MIGRATION_CROSS_PLATFORM.md`
- [ ] Update `CHANGELOG.md`
- [ ] Create troubleshooting guide: `docs/guides/TROUBLESHOOTING.md`
- [ ] Update API documentation

**Depends on:** P5.1
**Deliverable:** Updated documentation

#### P5.3: Release Preparation
- [ ] Version bump
- [ ] Release notes
- [ ] CI/CD pipeline updates (Windows/Linux runners)
- [ ] Package distribution (Windows wheels, Linux packages)

**Depends on:** P5.1, P5.2
**Deliverable:** Release-ready code

---

### Phase 6: Remote Compute
**Goal:** `thegent run --remote` for cross-host execution (Mac→Windows, etc.)
**Duration:** 1 week
**Effort:** 15-25 tool calls, 2-3 parallel subagents, ~8-12 min
**Extends:** [REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md](./REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md), HYBRID_ENV Phase 4

#### P6.1: Remote Host Configuration
- [ ] Create `RemoteHost` dataclass and `load_remote_hosts()` in `src/thegent/infra/remote_hosts.py`
- [ ] Add `~/.thegent/remote_hosts.yaml` schema and validation (Pydantic)
- [ ] Path mapping: resolve local path to remote path per host config
- [ ] Unit tests: `tests/test_remote_hosts.py`

**Depends on:** None
**Deliverable:** Remote host config + validation

#### P6.2: Remote Execution
- [ ] Implement `run_remote(host, cwd, prompt, agent)` via paramiko or subprocess+ssh
- [ ] Implement `ps_remote(host)`, `logs_remote(host, session_id)`, `stop_remote`, `wait_remote`
- [ ] Add `--remote HOST` to `run`, `bg`, `ps`, `logs`, `stop`, `wait` in CLI
- [ ] Stream output back to client
- [ ] Unit tests: `tests/test_remote_execution.py`

**Depends on:** P6.1
**Deliverable:** Remote run/ps/logs/stop/wait

#### P6.3: Documentation
- [ ] Document in `docs/guides/HYBRID_ENV_QUICK_START.md` and CLI help
- [ ] Add remote_hosts.yaml example to docs

**Depends on:** P6.2
**Deliverable:** Docs + examples

---

### Phase 7: OS-Level Agent Primitives
**Goal:** Resource containment and agents-as-OS-principals (cgroups, Job Objects, systemd scope)
**Duration:** 1-2 weeks
**Effort:** 20-35 tool calls, 3-4 parallel subagents, ~12-18 min
**Extends:** [AGENT_OS_PRINCIPALS_DEPTH.md](../reference/AGENT_OS_PRINCIPALS_DEPTH.md), CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH §4-5

#### P7.1: Linux systemd Scope
- [ ] Add `isolation_mode=systemd-scope` option for Linux
- [ ] Implement `systemd-run --scope -p MemoryMax=... -p CPUQuota=... -- thegent run ...`
- [ ] Config: `resource_limits.memory_mb`, `resource_limits.cpu_percent`
- [ ] Unit tests: `tests/test_systemd_scope.py` (mock or skip if no systemd)

**Depends on:** P1.5 (AgentRunner Integration)
**Deliverable:** Linux resource containment via systemd

#### P7.2: Windows Job Objects
- [ ] Add `isolation_mode=job-object` option for Windows
- [ ] Implement `CreateJobObject`, `AssignProcessToJobObject` with memory/CPU limits
- [ ] Use ctypes or pywin32; fallback to sub-user if unavailable
- [ ] Unit tests: `tests/test_windows_job_objects.py` (Windows only)

**Depends on:** P1.5
**Deliverable:** Windows resource containment via Job Objects

#### P7.3: macOS Resource Limits (Optional)
- [ ] Document launchd per-agent option (future)
- [ ] Add `resource_limits` config schema for parity; no implementation yet

**Depends on:** P1.6
**Deliverable:** Config schema + docs

#### P7.4: Integration and Docs
- [ ] Wire P7.1, P7.2 into AgentRunner based on `isolation_mode`
- [ ] Update `docs/reference/AGENT_OS_PRINCIPALS_DEPTH.md` with implementation status
- [ ] Add troubleshooting for "systemd not found", "Job Object failed"

**Depends on:** P7.1, P7.2
**Deliverable:** Integrated resource containment + docs

---

### Phase 8: Polish, Optimization & Extensions
**Goal:** Wider scope, deeper failure handling, UX polish, optimization
**Duration:** 2-3 weeks
**Effort:** 35-50 tool calls, 4-5 parallel subagents, ~18-25 min
**Extends:** [CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md](../research/CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md)

#### P8.1: Error Taxonomy & Structured Errors
- [ ] Define error code schema (THGENT-E001..E099)
- [ ] Add structured error types with codes, causes, doc links
- [ ] Create `docs/reference/ERROR_CODES.md`
- [ ] Wire into desktop automation, remote, hooks

**Depends on:** P5.1
**Deliverable:** Error codes + ERROR_CODES.md

#### P8.2: Diagnostic Commands
- [ ] Add `thegent diagnose permissions` (accessibility, UIA, AT-SPI)
- [ ] Add `thegent diagnose remote HOST` (SSH, path mapping, version)
- [ ] Add `thegent diagnose element SEL` (find attempt, tree snippet)
- [ ] Add `thegent diagnose shell` (shell selection for all contexts)

**Depends on:** P5.1, P6.2
**Deliverable:** `thegent diagnose` subcommands

#### P8.3: Troubleshooting Runbooks
- [ ] Create `docs/guides/TROUBLESHOOTING_DESKTOP_AUTOMATION.md`
- [ ] Create `docs/guides/TROUBLESHOOTING_REMOTE.md`
- [ ] Create `docs/guides/TROUBLESHOOTING_HOOKS.md`
- [ ] Cross-link from error messages

**Depends on:** P8.1
**Deliverable:** Runbooks + cross-links

#### P8.4: Circuit Breaker & Retry
- [ ] Add circuit breaker for desktop provider (tenacity/pybreaker)
- [ ] Add circuit breaker for remote host connections
- [ ] Implement retry/fallback chains (automation, remote, element find)
- [ ] Integrate with existing retry system (WP-2002)

**Depends on:** P3.5, P6.2
**Deliverable:** Circuit breaker + retry chains

#### P8.5: Optimization
- [ ] SSH connection pooling for remote (`ps`, `logs`, `stop` reuse)
- [ ] Add `thegent warmup` + `warmup_on_start` config
- [ ] Element cache TTL + event-based invalidation
- [ ] OTel spans + trace_id propagation for automation/remote

**Depends on:** P6.2, P3.5
**Deliverable:** Pooling, warmup, OTel

#### P8.6: Headless & Edge Cases
- [ ] Add `--headless` flag and `THGENT_HEADLESS=1`
- [ ] Skip user activity check when headless; mock UserActivityDetector
- [ ] Create `docs/guides/HEADLESS_AND_CI.md`
- [ ] Multi-monitor, high-DPI, locked-screen detection (optional)

**Depends on:** P1.5, P2.2
**Deliverable:** Headless mode + docs

#### P8.7: WSL2 & Platform Extensions
- [ ] WSL2 path translation (`/mnt/c/` ↔ `C:\`) for remote
- [ ] Document FreeBSD as unsupported; add platform detection
- [ ] Wayland notes in Linux provider docs

**Depends on:** P1.7, P3.3, P6.1
**Deliverable:** WSL2 support + platform docs

---

## Dependencies Graph

```
P1.1 (SystemUser)
  ├─> P1.2 (OS User macOS/Linux)
  │     └─> P1.4 (User Pool)
  ├─> P1.3 (OS User Windows)
  │     └─> P1.4 (User Pool)
  ├─> P1.5 (AgentRunner Integration)
  │     └─> P1.6 (Configuration)
  └─> P1.7 (Shell Strategy)
        └─> P2.7 (Hook Dispatcher Shell)

P2.1 (Tenant-Aware Lease)
  └─> P2.5 (Conflict Resolver)

P2.2 (User Activity)
  └─> P2.3 (Desktop Coordinator)
        └─> P2.5 (Conflict Resolver)

P2.4 (Tenant Concurrency)
  └─> P2.6 (Configuration)

P3.1 (Desktop Automation Base)
  ├─> P3.2 (macOS Provider)
  ├─> P3.3 (Windows Provider)
  └─> P3.4 (Linux Provider)
        └─> P3.5 (Cross-Platform Testing)

P4.1 (MCP Tools)
  ├─> P4.2 (MCP Resources)
  └─> P4.3 (Examples)

P5.1 (Testing)
  ├─> P5.2 (Documentation)
  └─> P5.3 (Release)

P6.1 (Remote Host Config)
  └─> P6.2 (Remote Execution)
        └─> P6.3 (Remote Docs)

P7.1 (systemd Scope)
  └─> P7.4 (Integration)

P7.2 (Job Objects)
  └─> P7.4 (Integration)

P7.3 (macOS docs)
  └─> P7.4 (Integration)

P8.1 (Error Taxonomy)
  ├─> P8.2 (Diagnostics)
  └─> P8.3 (Runbooks)

P8.4 (Circuit Breaker)
  └─> P8.5 (Optimization)

P5.1, P6.2
  └─> P8.2, P8.4, P8.5

P8.6 (Headless)
  └─> (standalone)

P8.7 (WSL2)
  └─> (standalone)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **OS user creation requires root/admin** | Make it opt-in (sub-user default), document requirements |
| **Desktop automation permissions** | Clear documentation, permission check utilities |
| **Platform API differences** | Abstract layer, platform-specific tests |
| **Performance overhead** | Benchmarking, optimization, caching |
| **User experience disruption** | User activity detection, coordination locks |

---

## Success Criteria

- [ ] Agents can run with sub-user or OS user isolation
- [ ] Multi-tenant coordination prevents conflicts
- [ ] Desktop automation works on macOS, Linux, Windows
- [ ] MCP tools expose desktop automation
- [ ] Remote compute (`thegent run --remote`) works
- [ ] OS-level primitives (systemd scope, Job Objects) available
- [ ] Diagnostic commands and runbooks available
- [ ] All tests pass on all platforms
- [ ] Documentation is complete

---

---

## Additional Considerations (From Extended Research)

### CUA Integration Evaluation

**Discovery:** CUA (Computer-Use Agent) provides comprehensive desktop automation framework with MCP support.

**Decision Point:** Evaluate CUA integration vs native implementation.

**Tasks:**
- [ ] Evaluate CUA MCP server (`libs/mcp-server`)
- [ ] Test CUA Computer SDK (`cua-computer`)
- [ ] Compare CUA vs native providers (performance, features)
- [ ] Decision: Use CUA, native, or hybrid approach

**Timeline:** During Phase 3 (Desktop Automation Primitives)

### Advanced Patterns Integration

**From:** `docs/research/CROSS_PLATFORM_ADVANCED_PATTERNS.md`

**Considerations:**
- Circuit breaker pattern for automation failures
- Distributed lock coordination (if multi-machine)
- Event-driven coordination (reduce polling overhead)
- Adaptive timeout strategy
- Property-based testing

**Tasks:**
- [ ] Review advanced patterns document
- [ ] Select patterns to implement (based on requirements)
- [ ] Integrate selected patterns into implementation

**Timeline:** Phase 5 (Testing & Polish) or future phases

### Integration with Existing Systems

**Existing thegent Systems:**
- `ConcurrencyController` (WP-5001) — Extend with tenant-aware limits
- `EditLeaseManager` (MTSP-14) — Extend with tenant awareness
- Retry & Fallback (WP-2002) — Use for automation failures
- Run Registry — Log automation actions
- OpenTelemetry — Add automation spans

**Tasks:**
- [ ] Extend ConcurrencyController with tenant limits (Phase 2)
- [ ] Extend EditLeaseManager with tenant awareness (Phase 2)
- [ ] Integrate automation retry with existing retry system (Phase 4)
- [ ] Add automation events to run registry (Phase 4)
- [ ] Add OTel spans for automation (Phase 4)

**Timeline:** Throughout implementation phases

---

**Status:** Ready for implementation. Extended with CUA evaluation and advanced patterns.
