# Hybrid Mac/Windows Environment Implementation Plan

**Status:** Planning | **Date:** 2026-02-16
**Related:** [Architecture Document](../architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md)

---

## Overview

This plan breaks down the hybrid Mac/Windows development environment setup into actionable tasks with dependencies, estimates, and acceptance criteria.

---

## Phase 1: Foundation Setup (Week 1)

### P1.1 Windows PC Initial Setup

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.1.1 | Install Syncthing on Windows | 15 min | None |
| P1.1.2 | Create `D:\kush\` directory structure | 10 min | None |
| P1.1.3 | Configure Syncthing folder: `D:\kush\` | 10 min | P1.1.1, P1.1.2 |
| P1.1.4 | Install Tailscale on Windows | 10 min | None |
| P1.1.5 | Configure Tailscale and get device IP | 5 min | P1.1.4 |
| P1.1.6 | Install Parsec host on Windows | 10 min | None |
| P1.1.7 | Configure Parsec hosting and access code | 10 min | P1.1.6 |
| P1.1.8 | Install WSL2 (Ubuntu) | 30 min | None |
| P1.1.9 | Configure WSL2 with basic tools | 20 min | P1.1.8 |
| P1.1.10 | Test Windows firewall rules | 10 min | P1.1.1, P1.1.4, P1.1.6 |

**Acceptance Criteria:**
- Syncthing web UI accessible at `http://localhost:8384`
- Tailscale device shows as connected
- Parsec hosting enabled with access code
- WSL2 Ubuntu terminal working
- Firewall allows Syncthing (22000), Parsec (8000-8010), SSH (22)

**Total Estimate:** ~2 hours

---

### P1.2 Mac Initial Setup

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.2.1 | Install Syncthing on Mac (Homebrew) | 10 min | None |
| P1.2.2 | Create `~/kush/` directory structure | 10 min | None |
| P1.2.3 | Configure Syncthing folder: `~/kush/` | 10 min | P1.2.1, P1.2.2 |
| P1.2.4 | Install Tailscale on Mac | 10 min | None |
| P1.2.5 | Connect Mac to Tailscale network | 5 min | P1.2.4, P1.1.5 |
| P1.2.6 | Install Parsec client on Mac | 10 min | None |
| P1.2.7 | Test Parsec connection to Windows PC | 15 min | P1.2.6, P1.1.7 |
| P1.2.8 | Verify Tailscale connectivity (ping test) | 5 min | P1.2.5 |

**Acceptance Criteria:**
- Syncthing web UI accessible at `http://localhost:8384`
- Mac and Windows show as connected in Tailscale
- Parsec connection successful (<20ms latency)
- Ping from Mac to Windows PC successful

**Total Estimate:** ~1.5 hours

---

### P1.3 Device Pairing

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.3.1 | Exchange Syncthing device IDs (Mac ↔ Windows) | 10 min | P1.1.3, P1.2.3 |
| P1.3.2 | Create shared folder `kush` in Syncthing | 10 min | P1.3.1 |
| P1.3.3 | Configure folder sync settings | 15 min | P1.3.2 |
| P1.3.4 | Test initial sync (create test file) | 10 min | P1.3.3 |
| P1.3.5 | Verify bi-directional sync working | 10 min | P1.3.4 |

**Acceptance Criteria:**
- Both devices show as "Connected" in Syncthing
- Test file created on Mac appears on Windows
- Test file created on Windows appears on Mac
- Sync completes in <30 seconds for small files

**Total Estimate:** ~1 hour

**Phase 1 Total:** ~4.5 hours

---

## Phase 2: Sync Configuration (Week 2)

### P2.1 Sync Ignore Patterns

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.1.1 | Create `.stignore` file template | 15 min | P1.3.2 |
| P2.1.2 | Add Git ignore patterns (`.git/`, `.gitignore`) | 10 min | P2.1.1 |
| P2.1.3 | Add build artifact patterns (`dist/`, `build/`, `target/`) | 10 min | P2.1.1 |
| P2.1.4 | Add dependency patterns (`node_modules/`, `.venv/`, `vendor/`) | 10 min | P2.1.1 |
| P2.1.5 | Add OS-specific patterns (`.DS_Store`, `Thumbs.db`, `__pycache__/`) | 10 min | P2.1.1 |
| P2.1.6 | Add cache patterns (`.cache/`, `.local/`) | 10 min | P2.1.1 |
| P2.1.7 | Test ignore patterns (verify excluded files don't sync) | 15 min | P2.1.6 |

**Acceptance Criteria:**
- `.stignore` file created in `kush/` root
- Excluded files don't appear in sync
- Sync performance improved (fewer files)

**Total Estimate:** ~1.5 hours

---

### P2.2 Sync Versioning & Conflict Resolution

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.2.1 | Configure Syncthing versioning (30 days, simple) | 10 min | P1.3.2 |
| P2.2.2 | Create conflict resolution script | 30 min | P2.2.1 |
| P2.2.3 | Test conflict scenario (simultaneous edit) | 20 min | P2.2.2 |
| P2.2.4 | Verify versioning working (check `.stversions/`) | 10 min | P2.2.1 |

**Acceptance Criteria:**
- Versioning enabled (30 days retention)
- Conflicts create `.sync-conflict-*` files
- Conflict resolution script works
- Old versions accessible in `.stversions/`

**Total Estimate:** ~1.5 hours

---

### P2.3 Config Directory Structure

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.3.1 | Create `kush/configs/` directory structure | 15 min | P1.3.2 |
| P2.3.2 | Create subdirectories (shell, vscode, cursor, nvim, git, docker, task) | 10 min | P2.3.1 |
| P2.3.3 | Create platform-specific directories (mac, windows, wsl) | 5 min | P2.3.1 |
| P2.3.4 | Initialize Git repo in `kush/configs/` | 10 min | P2.3.1 |
| P2.3.5 | Create `.gitignore` for configs | 5 min | P2.3.4 |

**Acceptance Criteria:**
- Directory structure created
- Git repo initialized
- Structure documented

**Total Estimate:** ~1 hour

---

### P2.4 Shell Config Sync

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.4.1 | Backup existing shell configs (`.zshrc`, `.bashrc`) | 10 min | None |
| P2.4.2 | Create platform-detection functions | 20 min | P2.3.2 |
| P2.4.3 | Move shell configs to `kush/configs/shell/` | 15 min | P2.4.1, P2.3.2 |
| P2.4.4 | Create symlinks (Mac: `~/.zshrc` → `~/kush/configs/shell/.zshrc`) | 10 min | P2.4.3 |
| P2.4.5 | Create symlinks (Windows WSL: `~/.bashrc` → `~/kush/configs/shell/.bashrc`) | 10 min | P2.4.3 |
| P2.4.6 | Test shell configs on both platforms | 15 min | P2.4.4, P2.4.5 |
| P2.4.7 | Sync and verify configs appear on both platforms | 10 min | P2.4.6 |

**Acceptance Criteria:**
- Shell configs syncing correctly
- Platform-specific sections working
- Symlinks working on both platforms

**Total Estimate:** ~1.5 hours

---

### P2.5 Editor Config Sync

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.5.1 | Backup VS Code settings | 10 min | None |
| P2.5.2 | Move VS Code settings to `kush/configs/vscode/` | 15 min | P2.3.2 |
| P2.5.3 | Create symlink/junction (Mac: `~/Library/Application Support/Code/User` → `~/kush/configs/vscode/`) | 10 min | P2.5.2 |
| P2.5.4 | Create symlink/junction (Windows: `%APPDATA%\Code\User` → `D:\kush\configs\vscode\`) | 10 min | P2.5.2 |
| P2.5.5 | Backup Cursor settings | 10 min | None |
| P2.5.6 | Move Cursor settings to `kush/configs/cursor/` | 15 min | P2.3.2 |
| P2.5.7 | Create symlinks for Cursor configs | 10 min | P2.5.6 |
| P2.5.8 | Test editor configs on both platforms | 15 min | P2.5.3, P2.5.4, P2.5.7 |

**Acceptance Criteria:**
- VS Code settings syncing
- Cursor settings syncing
- Extensions list syncing (if applicable)
- Keybindings working on both platforms

**Total Estimate:** ~1.5 hours

---

### P2.6 Terminal Config Sync

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.6.1 | Backup iTerm2 settings (Mac) | 10 min | None |
| P2.6.2 | Export iTerm2 profiles to `kush/configs/iterm2/` | 15 min | P2.3.2 |
| P2.6.3 | Backup Windows Terminal settings | 10 min | None |
| P2.6.4 | Export Windows Terminal settings to `kush/configs/windows-terminal/` | 15 min | P2.3.2 |
| P2.6.5 | Backup WSL terminal configs | 10 min | None |
| P2.6.6 | Move WSL configs to `kush/configs/wsl/` | 15 min | P2.3.2 |
| P2.6.7 | Create import scripts for terminal configs | 30 min | P2.6.2, P2.6.4, P2.6.6 |
| P2.6.8 | Test terminal configs on both platforms | 20 min | P2.6.7 |

**Acceptance Criteria:**
- Terminal configs syncing
- Profiles working on both platforms
- Themes/colors syncing

**Total Estimate:** ~2 hours

**Phase 2 Total:** ~9 hours

---

## Phase 3: Project Migration (Week 3)

### P3.1 Project Directory Setup

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.1.1 | Create `kush/projects/` directory | 5 min | P1.3.2 |
| P3.1.2 | Move `thegent/` to `D:\kush\projects\thegent\` (Windows) | 30 min | P3.1.1 |
| P3.1.3 | Update Git remote paths if needed | 10 min | P3.1.2 |
| P3.1.4 | Verify Git working in new location | 10 min | P3.1.3 |
| P3.1.5 | Move other projects to `kush/projects/` | 1 hour | P3.1.1 |
| P3.1.6 | Verify all projects syncing | 15 min | P3.1.5 |

**Acceptance Criteria:**
- All projects in `kush/projects/`
- Git repos working
- Projects syncing to Mac

**Total Estimate:** ~2 hours

---

### P3.2 Dependency Management

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.2.1 | Document platform-specific dependencies | 30 min | P3.1.6 |
| P3.2.2 | Create setup scripts per-platform | 1 hour | P3.2.1 |
| P3.2.3 | Test Python venv recreation (Mac) | 20 min | P3.2.2 |
| P3.2.4 | Test Python venv recreation (Windows) | 20 min | P3.2.2 |
| P3.2.5 | Test Node.js `node_modules` recreation | 20 min | P3.2.2 |
| P3.2.6 | Test Rust `target/` recreation | 20 min | P3.2.2 |
| P3.2.7 | Create dependency sync verification script | 30 min | P3.2.2 |

**Acceptance Criteria:**
- Setup scripts working on both platforms
- Dependencies recreating correctly
- Verification script passing

**Total Estimate:** ~3 hours

---

### P3.3 Build Verification

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.3.1 | Test `thegent` build on Windows | 30 min | P3.1.2 |
| P3.3.2 | Test `thegent` build on Mac | 30 min | P3.1.6 |
| P3.3.3 | Fix platform-specific build issues | 1 hour | P3.3.1, P3.3.2 |
| P3.3.4 | Test other project builds | 1 hour | P3.1.5 |
| P3.3.5 | Document platform-specific build notes | 30 min | P3.3.3, P3.3.4 |

**Acceptance Criteria:**
- All projects building on Windows
- All projects building on Mac
- Build issues documented

**Total Estimate:** ~3.5 hours

**Phase 3 Total:** ~8.5 hours

---

## Phase 4: Compute Offloading (Week 4)

**Extended by:** [REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md](./REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md) — full spec for `thegent run --remote`, `remote_hosts.yaml`, path mapping.

### P4.1 SSH Setup

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.1.1 | Enable OpenSSH Server on Windows | 15 min | None |
| P4.1.2 | Configure SSH key-based auth | 20 min | P4.1.1 |
| P4.1.3 | Generate SSH key pair on Mac | 10 min | None |
| P4.1.4 | Copy SSH public key to Windows | 10 min | P4.1.2, P4.1.3 |
| P4.1.5 | Test SSH connection (Mac → Windows) | 10 min | P4.1.4 |
| P4.1.6 | Configure SSH config (`~/.ssh/config`) | 15 min | P4.1.5 |
| P4.1.7 | Test remote command execution | 15 min | P4.1.6 |

**Acceptance Criteria:**
- SSH connection working (key-based auth)
- Remote commands executing
- SSH config configured

**Total Estimate:** ~1.5 hours

---

### P4.2 Remote Execution Integration

**Full spec:** [REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md](./REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md) — `thegent run --remote`, `remote_hosts.yaml`, path mapping.

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.2.1 | Research `thegent` remote execution capabilities | 30 min | None |
| P4.2.2 | Create remote execution wrapper script | 1 hour | P4.1.7 |
| P4.2.3 | Test `thegent run --remote windows-pc` | 30 min | P4.2.2 |
| P4.2.4 | Integrate with existing `thegent` CLI | 1 hour | P4.2.3 |
| P4.2.5 | Document remote execution usage | 30 min | P4.2.4 |

**Acceptance Criteria:**
- Remote execution working
- CLI integration complete
- Documentation complete

**Total Estimate:** ~3.5 hours

---

### P4.3 Service Migration

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.3.1 | Install Docker Desktop on Windows | 20 min | None |
| P4.3.2 | Configure Docker Desktop settings | 15 min | P4.3.1 |
| P4.3.3 | Install process-compose on Windows | 15 min | None |
| P4.3.4 | Move dev services to Windows (process-compose.yaml) | 30 min | P4.3.3 |
| P4.3.5 | Test services running on Windows | 30 min | P4.3.4 |
| P4.3.6 | Configure port forwarding (if needed) | 20 min | P4.3.5 |
| P4.3.7 | Test remote service access from Mac | 20 min | P4.3.6 |

**Acceptance Criteria:**
- Docker Desktop working
- process-compose services running
- Services accessible from Mac

**Total Estimate:** ~2.5 hours

---

### P4.4 Heavy Compute Testing

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.4.1 | Test large build on Windows (thegent) | 30 min | P3.3.1 |
| P4.4.2 | Test parallel test execution on Windows | 30 min | P4.4.1 |
| P4.4.3 | Benchmark build times (Mac vs Windows) | 30 min | P4.4.1 |
| P4.4.4 | Document performance improvements | 20 min | P4.4.3 |

**Acceptance Criteria:**
- Builds running successfully
- Performance improvements documented
- Benchmarks recorded

**Total Estimate:** ~2 hours

**Phase 4 Total:** ~9.5 hours

---

## Phase 5: Optimization & Polish (Week 5)

### P5.1 Sync Performance Optimization

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.1.1 | Configure sync bandwidth limits | 15 min | P1.3.2 |
| P5.1.2 | Set up sync schedule (off-hours full sync) | 15 min | P5.1.1 |
| P5.1.3 | Configure selective sync for large files | 30 min | P5.1.1 |
| P5.1.4 | Test sync performance with optimizations | 30 min | P5.1.3 |
| P5.1.5 | Document sync performance metrics | 20 min | P5.1.4 |

**Acceptance Criteria:**
- Sync bandwidth optimized
- Large files handled correctly
- Performance metrics documented

**Total Estimate:** ~2 hours

---

### P5.2 Parsec Optimization

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.2.1 | Optimize Parsec settings (resolution, FPS) | 20 min | P1.1.7 |
| P5.2.2 | Configure hardware encoding (NVENC) | 15 min | P5.2.1 |
| P5.2.3 | Test Parsec latency and FPS | 20 min | P5.2.2 |
| P5.2.4 | Fine-tune adaptive quality settings | 20 min | P5.2.3 |
| P5.2.5 | Document optimal Parsec settings | 15 min | P5.2.4 |

**Acceptance Criteria:**
- Parsec latency <20ms
- FPS >60
- Settings documented

**Total Estimate:** ~1.5 hours

---

### P5.3 Backup Automation

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.3.1 | Create backup script (Windows) | 1 hour | None |
| P5.3.2 | Set up Windows Task Scheduler (daily backups) | 30 min | P5.3.1 |
| P5.3.3 | Test backup script | 20 min | P5.3.2 |
| P5.3.4 | Configure backup retention (30 days) | 15 min | P5.3.3 |
| P5.3.5 | Test backup restoration | 30 min | P5.3.4 |

**Acceptance Criteria:**
- Daily backups running
- Backup retention working
- Restoration tested

**Total Estimate:** ~2.5 hours

---

### P5.4 Documentation

**Tasks:**

| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.4.1 | Create setup guide for new machines | 2 hours | All phases |
| P5.4.2 | Create troubleshooting guide | 1.5 hours | All phases |
| P5.4.3 | Document platform-specific notes | 1 hour | P3.3.5 |
| P5.4.4 | Create runbooks for common tasks | 1 hour | All phases |
| P5.4.5 | Update architecture document with lessons learned | 30 min | All phases |

**Acceptance Criteria:**
- Setup guide complete
- Troubleshooting guide complete
- Platform notes documented
- Runbooks created

**Total Estimate:** ~6 hours

**Phase 5 Total:** ~12 hours

---

## Summary

| Phase | Duration | Total Hours | Key Deliverables |
|-------|----------|-------------|------------------|
| **Phase 1: Foundation** | Week 1 | ~4.5 hours | Basic sync and remote access |
| **Phase 2: Sync Config** | Week 2 | ~9 hours | Full config sync |
| **Phase 3: Project Migration** | Week 3 | ~8.5 hours | All projects syncing |
| **Phase 4: Compute Offloading** | Week 4 | ~9.5 hours | Remote execution working |
| **Phase 5: Optimization** | Week 5 | ~12 hours | Production-ready setup |
| **Total** | **5 weeks** | **~43.5 hours** | Complete hybrid environment |

---

## Risk Mitigation

### High-Risk Items

1. **Sync Conflicts**
   - Mitigation: Git-based conflict resolution, versioning
   - Contingency: Manual conflict resolution process

2. **Network Connectivity**
   - Mitigation: Tailscale VPN + direct LAN fallback
   - Contingency: Cloud relay servers

3. **Performance Issues**
   - Mitigation: Selective sync, bandwidth limits
   - Contingency: Resilio Sync (paid alternative)

4. **Data Loss**
   - Mitigation: Versioning, backups, Git repos
   - Contingency: Restore from backups

---

## Dependencies

### External Dependencies

- Syncthing: Available, free
- Tailscale: Available, free (up to 100 devices)
- Parsec: Available, free (personal use)
- WSL2: Built into Windows 11

### Internal Dependencies

- Git repositories: Already in place
- Project structure: Needs migration
- Config files: Need backup and migration

---

## Success Metrics

### Phase 1 Success
- [ ] Syncthing devices connected
- [ ] Parsec connection <20ms latency
- [ ] Tailscale mesh working

### Phase 2 Success
- [ ] Configs syncing correctly
- [ ] Conflict resolution working
- [ ] Versioning enabled

### Phase 3 Success
- [ ] All projects syncing
- [ ] Builds working on both platforms
- [ ] Dependencies managed correctly

### Phase 4 Success
- [ ] SSH working
- [ ] Remote execution working
- [ ] Services running on Windows

### Phase 5 Success
- [ ] Performance optimized
- [ ] Backups automated
- [ ] Documentation complete

---

## 7. Configuration Examples

### 7.1 Syncthing Setup Example

```bash
# Step 1: Install Syncthing on both devices
# Windows (download from https://syncthing.net/downloads/)
# Mac: brew install syncthing

# Step 2: Start Syncthing
# Windows: Run as service or startup app
# Mac: syncthing

# Step 3: Access web UI
# http://localhost:8384

# Step 4: Pair devices (exchange Device IDs)
# Mac Device ID: <mac-device-id-here>
# Windows Device ID: <windows-device-id-here>
```

### 7.2 SSH Key Setup Example

```bash
# Step 1: Generate SSH key on Mac
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_windows -C "developer@macbook"

# Step 2: Copy public key to Windows
ssh-copy-id -i ~/.ssh/id_ed25519_windows.pub developer@windows-pc-ip

# Step 3: Test connection
ssh -i ~/.ssh/id_ed25519_windows developer@windows-pc-ip

# Step 4: Add to SSH config (see 18.3 in architecture doc)
```

### 7.3 Tailscale Setup Example

```bash
# Step 1: Install Tailscale on both devices
# Windows: Download from https://tailscale.com/download
# Mac: brew install tailscale

# Step 2: Authenticate
# Windows: Sign in with GitHub/Google account
# Mac: tailscale up

# Step 3: Verify connection
tailscale status
tailscale ip -4

# Step 4: Configure ACLs (optional)
# See 18.4 in architecture doc
```

### 7.4 Parsec Setup Example

```bash
# Step 1: Download and install Parsec
# Windows: https://parsec.app/get
# Mac: brew install --cask parsec

# Step 2: Configure Windows as host
# - Open Parsec app
# - Click "Host"
# - Set access code (remember this!)
# - Enable hardware encoding (NVENC recommended)

# Step 3: Connect from Mac
# - Open Parsec app
# - Click "Connect"
# - Enter access code or select host
# - Configure display settings (resolution, FPS)

# Step 4: Optimize settings (see 9.2 in architecture doc)
```

### 7.5 Config Sync Example

```bash
# Step 1: Create configs directory
mkdir -p ~/kush/configs/{shell,vscode,cursor,nvim,git,docker,task}

# Step 2: Initialize Git repo
cd ~/kush/configs
git init
git add .
git commit -m "Initial config sync setup"

# Step 3: Sync to Windows
rsync -avz ~/kush/configs/ developer@windows-pc:D:/kush/configs/

# Step 4: Create symlinks
# Mac: ln -s ~/kush/configs/shell/.zshrc ~/.zshrc
# Windows: mklink /J %APPDATA%/Code/User D:/kush/configs/vscode/
```

### 7.6 Project Migration Example

```bash
# Step 1: Stop all services on Mac
# - Close IDEs
# - Stop dev servers

# Step 2: Move project to new location
mv ~/thegent ~/kush/projects/thegent

# Step 3: Update Git remote
cd ~/kush/projects/thegent
git remote set-url origin /path/to/repo

# Step 4: Create symlink for backward compatibility
ln -s ~/kush/projects/thegent ~/thegent

# Step 5: Sync to Windows
rsync -avz --delete ~/kush/projects/thegent/ developer@windows-pc:D:/kush/projects/thegent/

# Step 6: Verify on Windows
cd D:/kush/projects/thegent
git status
```

### 7.7 Remote Execution Example

```bash
# SSH to Windows and run command
ssh developer@windows-pc-tailscale "cd D:/kush/thegent && task build"

# Run with output streaming
ssh -t developer@windows-pc-tailscale "cd D:/kush/thegent && task test"

# Use thegent remote execution
thegent run --remote windows-pc "Build project" gemini

# SCP file to Windows
scp -r ~/project developer@windows-pc:D:/kush/projects/

# SCP file from Windows
scp developer@windows-pc:D:/kush/build/artifacts.zip ./
```

### 7.8 Service Migration Example

```bash
# Step 1: Export services config from Mac
cat ~/thegent/process-compose.yaml

# Step 2: Copy to Windows
scp ~/thegent/process-compose.yaml developer@windows-pc:D:/kush/thegent/

# Step 3: Adjust paths for Windows
# - Change ~/ to D:/
# - Change /path/to to D:\path\to
# - Update port numbers if needed

# Step 4: Start services on Windows
ssh developer@windows-pc-tailscale "cd D:/kush/thegent && process-compose up -f process-compose.yaml"

# Step 5: Verify from Mac
curl http://localhost:3847/health  # MCP server
```

### 7.9 Verification Commands

```bash
# Verify Syncthing
curl http://localhost:8384/rest/noauth/health
# Expected: {"configurationOK":true,"deviceOK":true,"folderOK":true}

# Verify Tailscale
tailscale status
# Expected: List of connected devices with IPs

# Verify SSH
ssh -o BatchMode=yes -o ConnectTimeout=2 windows-pc-tailscale "echo OK"
# Expected: OK

# Verify Git sync
git remote -v
git status

# Verify project builds
cd ~/kush/projects/thegent
task build  # Mac build
ssh developer@windows-pc-tailscale "cd D:/kush/thegent && task build"  # Windows build
```

---

## 8. Cross-References

| Topic | Reference |
|-------|-----------|
| Architecture | `../architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md` |
| Quick Start | `../guides/HYBRID_ENV_QUICK_START.md` |
| Setup Checklist | `../checklists/HYBRID_ENV_SETUP_CHECKLIST.md` |
| TUI/Queue Design | `../research/USER_QUEUE_TUI_AND_AGENT_POLL.md` |
| Compute Offloading | `REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md` |

---

## 9. Extension Summary

### Added in This Extension

| Section | Description |
|---------|-------------|
| **7. Configuration Examples** | Added practical examples for Syncthing, SSH, Tailscale, Parsec, config sync, project migration, remote execution, service migration, and verification |
| **8. Cross-References** | Added links to related documentation |

### Key Example Patterns

| Example | Purpose |
|---------|---------|
| 7.1 Syncthing | Basic sync setup |
| 7.2 SSH Keys | Secure remote access |
| 7.3 Tailscale | VPN mesh network |
| 7.4 Parsec | Remote desktop |
| 7.5 Config Sync | Cross-platform configs |
| 7.6 Project Migration | Moving projects to shared location |
| 7.7 Remote Execution | Running commands on Windows |
| 7.8 Service Migration | Moving services to Windows |
| 7.9 Verification | Testing setup |

### Troubleshooting Quick Links

| Issue | Reference |
|-------|-----------|
| Sync conflicts | Architecture doc §14.1 |
| Parsec lag | Architecture doc §14.3 |
| Build failures | Architecture doc §14.4 |
| Network issues | Architecture doc §14.1 |

---

**Document Version:** 1.1
**Last Updated:** 2026-02-17
**Extension:** Configuration Examples, Cross-References, Extension Summary
