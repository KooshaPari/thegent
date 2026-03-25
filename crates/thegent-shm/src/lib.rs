use memmap2::MmapMut;
use once_cell::sync::Lazy;
use std::fs::OpenOptions;
use std::path::PathBuf;
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
use pyo3::prelude::*;

// Constants for SHM layout
const MAX_BREAKERS: usize = 256;
const SLOT_SIZE: usize = 256;
const MAX_PROVIDERS: usize = 32;
const PROVIDER_SLOT_SIZE: usize = 128;

const BREAKER_OFFSET: usize = 0;
const PROVIDER_OFFSET: usize = MAX_BREAKERS * SLOT_SIZE;
const XP_OFFSET: usize = PROVIDER_OFFSET + (MAX_PROVIDERS * PROVIDER_SLOT_SIZE);
const XP_SIZE: usize = 64;
const HEALTH_OFFSET: usize = XP_OFFSET + XP_SIZE;
const RESOURCE_OFFSET: usize = HEALTH_OFFSET + 64;
const RACE_OFFSET: usize = RESOURCE_OFFSET + 1024;
const RACE_COUNT: usize = 32;
const RACE_SLOT_SIZE: usize = 512;
const CMD_CACHE_OFFSET: usize = RACE_OFFSET + (RACE_COUNT * RACE_SLOT_SIZE);
const CMD_CACHE_COUNT: usize = 64;
const CMD_CACHE_SLOT_SIZE: usize = 512;
const ROUTER_METRICS_OFFSET: usize = CMD_CACHE_OFFSET + (CMD_CACHE_COUNT * CMD_CACHE_SLOT_SIZE);
const SHM_SIZE: usize = ROUTER_METRICS_OFFSET + 4096;

static GLOBAL_SHM: Lazy<Mutex<Option<SHMInterface>>> = Lazy::new(|| Mutex::new(None));
static PROVIDER_WRITE_LOCK: Lazy<Mutex<()>> = Lazy::new(|| Mutex::new(()));

#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct BreakerState {
    target: [u8; 128],
    category: i32,
    failures: u32,
    last_failure: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct ProviderState {
    pub name: [u8; 32],
    pub request_count: u64,
    pub success_count: u64,
    pub failure_count: u64,
    pub latency_p50_ms: u32,
    pub success_rate: f32,
    pub last_updated: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct XPState {
    pub total_xp: u64,
    pub level: u32,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct ResourceMetrics {
    pid: u32,
    cpu_usage: f32,
    memory_kb: u64,
    timestamp: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct RaceResult {
    pub race_id: [u8; 64],
    pub agent_id: [u8; 64],
    pub run_id: [u8; 64],
    pub status: [u8; 16],
    pub duration_ms: u64,
    pub score: f32,
    pub timestamp: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct CommandLock {
    pub cmd_hash: [u8; 64],
    pub pid: u32,
    pub status: [u8; 16],
    pub output_path: [u8; 256],
    pub start_time: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct RouterMetricsState {
    pub total_decisions: u64,
    pub lifecycle_count: u64,
    pub thegent_count: u64,
    pub route_changes: u64,
    pub hysteresis_activations: u64,
}

// ---------------------------------------------------------------------------
// Core SHM Interface struct (used by both Rust callers and PyO3)
// ---------------------------------------------------------------------------

#[cfg_attr(all(feature = "python", not(test), not(debug_assertions)), pyclass)]
pub struct SHMInterface {
    mmap: MmapMut,
}

impl SHMInterface {
    pub fn open(path: impl Into<PathBuf>) -> std::io::Result<Self> {
        let path = path.into();
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(&path)?;
        file.set_len(SHM_SIZE as u64)?;
        let mmap = unsafe { MmapMut::map_mut(&file)? };
        Ok(SHMInterface { mmap })
    }

    pub fn do_update_provider(
        &mut self,
        name: String,
        request_count: u64,
        success_count: u64,
        latency_ms: u32,
    ) -> std::io::Result<()> {
        let _guard = PROVIDER_WRITE_LOCK
            .lock()
            .map_err(|_| std::io::Error::other("provider write lock poisoned"))?;
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        let mut name_bytes = [0u8; 32];
        let len = name.len().min(32);
        name_bytes[..len].copy_from_slice(&name.as_bytes()[..len]);

        let success_rate = if request_count > 0 {
            success_count as f32 / request_count as f32
        } else {
            1.0
        };

        let new_state = ProviderState {
            name: name_bytes,
            request_count,
            success_count,
            failure_count: request_count.saturating_sub(success_count),
            latency_p50_ms: latency_ms,
            success_rate,
            last_updated: now,
        };

        let mut target_idx = None;
        for i in 0..MAX_PROVIDERS {
            let start = PROVIDER_OFFSET + (i * PROVIDER_SLOT_SIZE);
            let slot = &self.mmap[start..start + 32];
            if slot[0] == 0 {
                if target_idx.is_none() {
                    target_idx = Some(i);
                }
                continue;
            }
            if *slot == name_bytes {
                target_idx = Some(i);
                break;
            }
        }

        let idx = target_idx.ok_or_else(|| std::io::Error::other("Provider slots full"))?;
        let start = PROVIDER_OFFSET + (idx * PROVIDER_SLOT_SIZE);
        let end = start + std::mem::size_of::<ProviderState>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&new_state as *const ProviderState) as *const u8,
                std::mem::size_of::<ProviderState>(),
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    pub fn do_record_failure(&mut self, target: String, category: i32) -> std::io::Result<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        let target_bytes = target.as_bytes();
        let mut target_fixed = [0u8; 128];
        let len = target_bytes.len().min(128);
        target_fixed[..len].copy_from_slice(&target_bytes[..len]);

        let mut found_idx = None;
        let mut first_empty = None;

        for i in 0..MAX_BREAKERS {
            let start = BREAKER_OFFSET + (i * SLOT_SIZE);
            let end = start + std::mem::size_of::<BreakerState>();
            let slot = &self.mmap[start..end];
            let state: &BreakerState = unsafe { &*(slot.as_ptr() as *const BreakerState) };
            if state.target[0] == 0 {
                if first_empty.is_none() {
                    first_empty = Some(i);
                }
                continue;
            }
            if state.target == target_fixed && state.category == category {
                found_idx = Some((i, *state));
                break;
            }
        }

        let (idx, mut state) = if let Some((i, s)) = found_idx {
            (i, s)
        } else if let Some(i) = first_empty {
            (
                i,
                BreakerState {
                    target: target_fixed,
                    category,
                    failures: 0,
                    last_failure: 0.0,
                },
            )
        } else {
            return Err(std::io::Error::other("SHM Breaker slots full"));
        };

        state.failures += 1;
        state.last_failure = now;
        let start = BREAKER_OFFSET + (idx * SLOT_SIZE);
        let end = start + std::mem::size_of::<BreakerState>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&state as *const BreakerState) as *const u8,
                std::mem::size_of::<BreakerState>(),
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    pub fn do_award_xp(&mut self, amount: u64) -> std::io::Result<()> {
        let mut state = self.get_xp_state_internal();
        state.total_xp += amount;
        state.level = (state.total_xp / 1000) as u32 + 1;
        self.save_xp_state_internal(state)
    }

    pub fn do_set_health_score(&mut self, score: f64) -> std::io::Result<()> {
        let bytes = score.to_le_bytes();
        self.mmap[HEALTH_OFFSET..HEALTH_OFFSET + 8].copy_from_slice(&bytes);
        Ok(())
    }

    pub fn do_get_health_score(&self) -> f64 {
        let mut bytes = [0u8; 8];
        bytes.copy_from_slice(&self.mmap[HEALTH_OFFSET..HEALTH_OFFSET + 8]);
        f64::from_le_bytes(bytes)
    }

    pub fn do_record_resource_usage(
        &mut self,
        pid: u32,
        cpu_usage: f32,
        memory_kb: u64,
    ) -> std::io::Result<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        let state = ResourceMetrics {
            pid,
            cpu_usage,
            memory_kb,
            timestamp: now,
        };
        let start = RESOURCE_OFFSET;
        let end = RESOURCE_OFFSET + std::mem::size_of::<ResourceMetrics>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&state as *const ResourceMetrics) as *const u8,
                std::mem::size_of::<ResourceMetrics>(),
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    pub fn do_update_router_metrics(
        &mut self,
        lifecycle_inc: u64,
        thegent_inc: u64,
        changes_inc: u64,
        hysteresis_inc: u64,
    ) -> std::io::Result<()> {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        let metrics: &mut RouterMetricsState =
            unsafe { &mut *(self.mmap[start..end].as_ptr() as *mut RouterMetricsState) };
        metrics.total_decisions += lifecycle_inc + thegent_inc;
        metrics.lifecycle_count += lifecycle_inc;
        metrics.thegent_count += thegent_inc;
        metrics.route_changes += changes_inc;
        metrics.hysteresis_activations += hysteresis_inc;
        Ok(())
    }

    pub fn do_get_xp_state(&self) -> XPState {
        self.get_xp_state_internal()
    }

    pub fn do_get_provider_metrics(&self, name: &str) -> Option<ProviderState> {
        let mut name_bytes = [0u8; 32];
        let len = name.len().min(32);
        name_bytes[..len].copy_from_slice(&name.as_bytes()[..len]);
        for i in 0..MAX_PROVIDERS {
            let start = PROVIDER_OFFSET + (i * PROVIDER_SLOT_SIZE);
            let slot = &self.mmap[start..start + 32];
            if *slot == name_bytes {
                let end = start + std::mem::size_of::<ProviderState>();
                let state: &ProviderState =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const ProviderState) };
                return Some(*state);
            }
        }
        None
    }

    pub fn do_get_router_metrics(&self) -> RouterMetricsState {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        unsafe { *(self.mmap[start..end].as_ptr() as *const RouterMetricsState) }
    }

    fn get_xp_state_internal(&self) -> XPState {
        let start = XP_OFFSET;
        let end = start + std::mem::size_of::<XPState>();
        let slot = &self.mmap[start..end];
        let state: &XPState = unsafe { &*(slot.as_ptr() as *const XPState) };
        if state.level == 0 {
            return XPState {
                total_xp: 0,
                level: 1,
            };
        }
        *state
    }

    fn save_xp_state_internal(&mut self, state: XPState) -> std::io::Result<()> {
        let start = XP_OFFSET;
        let end = start + std::mem::size_of::<XPState>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&state as *const XPState) as *const u8,
                std::mem::size_of::<XPState>(),
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    // ========================================================================
    // Race Track Operations
    // ========================================================================

    /// Record a race result.
    ///
    /// # Arguments
    /// * `race_id` - Unique identifier for the race
    /// * `agent_id` - Agent that participated
    /// * `run_id` - Run identifier
    /// * `status` - Status string (e.g., "completed", "failed")
    /// * `duration_ms` - Duration in milliseconds
    /// * `score` - Score achieved
    pub fn do_record_race_result(
        &mut self,
        race_id: &str,
        agent_id: &str,
        run_id: &str,
        status: &str,
        duration_ms: u64,
        score: f32,
    ) -> std::io::Result<usize> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        let mut race_id_bytes = [0u8; 64];
        let mut agent_id_bytes = [0u8; 64];
        let mut run_id_bytes = [0u8; 64];
        let mut status_bytes = [0u8; 16];

        let race_len = race_id.len().min(64);
        let agent_len = agent_id.len().min(64);
        let run_len = run_id.len().min(64);
        let status_len = status.len().min(16);

        race_id_bytes[..race_len].copy_from_slice(&race_id.as_bytes()[..race_len]);
        agent_id_bytes[..agent_len].copy_from_slice(&agent_id.as_bytes()[..agent_len]);
        run_id_bytes[..run_len].copy_from_slice(&run_id.as_bytes()[..run_len]);
        status_bytes[..status_len].copy_from_slice(&status.as_bytes()[..status_len]);

        // Find first empty slot or slot with same race_id
        let mut target_idx = None;
        for i in 0..RACE_COUNT {
            let start = RACE_OFFSET + (i * RACE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if slot[0] == 0 {
                if target_idx.is_none() {
                    target_idx = Some(i);
                }
                continue;
            }
            if *slot == race_id_bytes {
                target_idx = Some(i);
                break;
            }
        }

        let idx = target_idx.ok_or_else(|| std::io::Error::other("Race result slots full"))?;

        let result = RaceResult {
            race_id: race_id_bytes,
            agent_id: agent_id_bytes,
            run_id: run_id_bytes,
            status: status_bytes,
            duration_ms,
            score,
            timestamp: now,
        };

        let start = RACE_OFFSET + (idx * RACE_SLOT_SIZE);
        let end = start + std::mem::size_of::<RaceResult>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&result as *const RaceResult) as *const u8,
                std::mem::size_of::<RaceResult>(),
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(idx)
    }

    /// Get a race result by index.
    pub fn do_get_race_result(&self, idx: usize) -> Option<RaceResult> {
        if idx >= RACE_COUNT {
            return None;
        }
        let start = RACE_OFFSET + (idx * RACE_SLOT_SIZE);
        let end = start + std::mem::size_of::<RaceResult>();
        let state: &RaceResult = unsafe { &*(self.mmap[start..end].as_ptr() as *const RaceResult) };
        if state.race_id[0] == 0 {
            return None;
        }
        Some(*state)
    }

    /// Find a race result by race_id.
    pub fn do_find_race_result(&self, race_id: &str) -> Option<(usize, RaceResult)> {
        let mut race_id_bytes = [0u8; 64];
        let len = race_id.len().min(64);
        race_id_bytes[..len].copy_from_slice(&race_id.as_bytes()[..len]);

        for i in 0..RACE_COUNT {
            let start = RACE_OFFSET + (i * RACE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if *slot == race_id_bytes {
                let end = start + std::mem::size_of::<RaceResult>();
                let state: &RaceResult =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const RaceResult) };
                return Some((i, *state));
            }
        }
        None
    }

    /// List all non-empty race results.
    pub fn do_list_race_results(&self) -> Vec<(usize, RaceResult)> {
        let mut results = Vec::new();
        for i in 0..RACE_COUNT {
            if let Some(result) = self.do_get_race_result(i) {
                results.push((i, result));
            }
        }
        results
    }

    /// Clear a race result by index.
    pub fn do_clear_race_result(&mut self, idx: usize) -> std::io::Result<()> {
        if idx >= RACE_COUNT {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                "Index out of range",
            ));
        }
        let start = RACE_OFFSET + (idx * RACE_SLOT_SIZE);
        self.mmap[start..start + RACE_SLOT_SIZE].fill(0);
        Ok(())
    }

    // ========================================================================
    // Command Cache Operations
    // ========================================================================

    /// Acquire a lock for a command execution.
    ///
    /// # Arguments
    /// * `cmd_hash` - Hash of the command to lock
    /// * `pid` - Process ID acquiring the lock
    ///
    /// # Returns
    /// The slot index where the lock was acquired, or error if slots are full
    /// or the command is already locked by another process.
    pub fn do_acquire_command_lock(&mut self, cmd_hash: &str, pid: u32) -> std::io::Result<usize> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        let mut cmd_hash_bytes = [0u8; 64];
        let len = cmd_hash.len().min(64);
        cmd_hash_bytes[..len].copy_from_slice(&cmd_hash.as_bytes()[..len]);

        // Check if already locked by another process
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if *slot == cmd_hash_bytes {
                let end = start + std::mem::size_of::<CommandLock>();
                let existing: &CommandLock =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const CommandLock) };
                if existing.pid != 0 && existing.pid != pid {
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::ResourceBusy,
                        "Command is locked by another process",
                    ));
                }
                // Same process can re-acquire (update lock)
                let lock = CommandLock {
                    cmd_hash: cmd_hash_bytes,
                    pid,
                    status: *b"running\0\0\0\0\0\0\0\0\0",
                    output_path: [0u8; 256],
                    start_time: now,
                };
                let bytes: &[u8] = unsafe {
                    std::slice::from_raw_parts(
                        (&lock as *const CommandLock) as *const u8,
                        std::mem::size_of::<CommandLock>(),
                    )
                };
                self.mmap[start..end].copy_from_slice(bytes);
                return Ok(i);
            }
        }

        // Find empty slot
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if slot[0] == 0 {
                let lock = CommandLock {
                    cmd_hash: cmd_hash_bytes,
                    pid,
                    status: *b"running\0\0\0\0\0\0\0\0\0",
                    output_path: [0u8; 256],
                    start_time: now,
                };
                let end = start + std::mem::size_of::<CommandLock>();
                let bytes: &[u8] = unsafe {
                    std::slice::from_raw_parts(
                        (&lock as *const CommandLock) as *const u8,
                        std::mem::size_of::<CommandLock>(),
                    )
                };
                self.mmap[start..end].copy_from_slice(bytes);
                return Ok(i);
            }
        }

        Err(std::io::Error::other("Command cache slots full"))
    }

    /// Release a command lock.
    pub fn do_release_command_lock(&mut self, cmd_hash: &str, pid: u32) -> std::io::Result<()> {
        let mut cmd_hash_bytes = [0u8; 64];
        let len = cmd_hash.len().min(64);
        cmd_hash_bytes[..len].copy_from_slice(&cmd_hash.as_bytes()[..len]);

        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if *slot == cmd_hash_bytes {
                let end = start + std::mem::size_of::<CommandLock>();
                let existing: &CommandLock =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const CommandLock) };
                if existing.pid != pid {
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::PermissionDenied,
                        "Lock owned by different process",
                    ));
                }
                self.mmap[start..start + CMD_CACHE_SLOT_SIZE].fill(0);
                return Ok(());
            }
        }

        Err(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "Command lock not found",
        ))
    }

    /// Get command lock status.
    pub fn do_get_command_lock(&self, cmd_hash: &str) -> Option<CommandLock> {
        let mut cmd_hash_bytes = [0u8; 64];
        let len = cmd_hash.len().min(64);
        cmd_hash_bytes[..len].copy_from_slice(&cmd_hash.as_bytes()[..len]);

        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if *slot == cmd_hash_bytes {
                let end = start + std::mem::size_of::<CommandLock>();
                let state: &CommandLock =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const CommandLock) };
                return Some(*state);
            }
        }
        None
    }

    /// Update command lock status and output path.
    pub fn do_update_command_lock(
        &mut self,
        cmd_hash: &str,
        pid: u32,
        status: &str,
        output_path: &str,
    ) -> std::io::Result<()> {
        let mut cmd_hash_bytes = [0u8; 64];
        let len = cmd_hash.len().min(64);
        cmd_hash_bytes[..len].copy_from_slice(&cmd_hash.as_bytes()[..len]);

        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if *slot == cmd_hash_bytes {
                let end = start + std::mem::size_of::<CommandLock>();
                let existing: &mut CommandLock =
                    unsafe { &mut *(self.mmap[start..end].as_mut_ptr() as *mut CommandLock) };
                if existing.pid != pid {
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::PermissionDenied,
                        "Lock owned by different process",
                    ));
                }

                // Update status
                let mut status_bytes = [0u8; 16];
                let status_len = status.len().min(16);
                status_bytes[..status_len].copy_from_slice(&status.as_bytes()[..status_len]);
                existing.status = status_bytes;

                // Update output path
                let mut path_bytes = [0u8; 256];
                let path_len = output_path.len().min(256);
                path_bytes[..path_len].copy_from_slice(&output_path.as_bytes()[..path_len]);
                existing.output_path = path_bytes;

                return Ok(());
            }
        }

        Err(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "Command lock not found",
        ))
    }

    /// List all active command locks.
    pub fn do_list_command_locks(&self) -> Vec<(usize, CommandLock)> {
        let mut locks = Vec::new();
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start + 64];
            if slot[0] != 0 {
                let end = start + std::mem::size_of::<CommandLock>();
                let state: &CommandLock =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const CommandLock) };
                if state.pid != 0 {
                    locks.push((i, *state));
                }
            }
        }
        locks
    }
}

// ---------------------------------------------------------------------------
// Global SHM management (usable from Rust without pyo3)
// ---------------------------------------------------------------------------

pub fn init_global_shm(path: &str) -> std::io::Result<()> {
    let interface = SHMInterface::open(path)?;
    let mut global = GLOBAL_SHM.lock().unwrap();
    *global = Some(interface);
    Ok(())
}

/// Update router metrics in global SHM.
///
/// If global SHM is not initialized, this is a no-op (returns Ok).
/// Callers should initialize SHM via `init_global_shm` before routing.
pub fn update_router_metrics(
    lifecycle_inc: u64,
    thegent_inc: u64,
    changes_inc: u64,
    hysteresis_inc: u64,
) -> std::io::Result<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(ref mut shm) = *global {
        shm.do_update_router_metrics(lifecycle_inc, thegent_inc, changes_inc, hysteresis_inc)
    } else {
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// PyO3 Python extension module (only compiled with --features python)
// ---------------------------------------------------------------------------

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pymethods]
impl SHMInterface {
    #[new]
    #[pyo3(signature = (path))]
    fn new(path: String) -> PyResult<Self> {
        SHMInterface::open(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
    }

    fn update_provider(
        &mut self,
        name: String,
        request_count: u64,
        success_count: u64,
        latency_ms: u32,
    ) -> PyResult<()> {
        self.do_update_provider(name, request_count, success_count, latency_ms)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn get_provider_metrics(&self, py: Python<'_>, name: String) -> PyResult<Option<PyObject>> {
        let mut name_bytes = [0u8; 32];
        let len = name.len().min(32);
        name_bytes[..len].copy_from_slice(&name.as_bytes()[..len]);

        for i in 0..MAX_PROVIDERS {
            let start = PROVIDER_OFFSET + (i * PROVIDER_SLOT_SIZE);
            let slot = &self.mmap[start..start + 32];
            if *slot == name_bytes {
                let end = start + std::mem::size_of::<ProviderState>();
                let state: &ProviderState =
                    unsafe { &*(self.mmap[start..end].as_ptr() as *const ProviderState) };

                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("request_count", state.request_count)?;
                dict.set_item("success_count", state.success_count)?;
                dict.set_item("latency_ms", state.latency_p50_ms)?;
                dict.set_item("success_rate", state.success_rate)?;
                dict.set_item("last_updated", state.last_updated)?;
                return Ok(Some(dict.into_any().unbind()));
            }
        }
        Ok(None)
    }

    fn record_failure(&mut self, target: String, category: i32) -> PyResult<()> {
        self.do_record_failure(target, category)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn award_xp(&mut self, amount: u64) -> PyResult<()> {
        self.do_award_xp(amount)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn get_xp_state(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let state = self.get_xp_state_internal();
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_xp", state.total_xp)?;
        dict.set_item("level", state.level)?;
        Ok(Some(dict.into_any().unbind()))
    }

    fn set_health_score(&mut self, score: f64) -> PyResult<()> {
        self.do_set_health_score(score)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn get_health_score(&self) -> PyResult<f64> {
        Ok(self.do_get_health_score())
    }

    fn record_resource_usage(&mut self, pid: u32, cpu_usage: f32, memory_kb: u64) -> PyResult<()> {
        self.do_record_resource_usage(pid, cpu_usage, memory_kb)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn update_router_metrics(
        &mut self,
        lifecycle_inc: u64,
        thegent_inc: u64,
        changes_inc: u64,
        hysteresis_inc: u64,
    ) -> PyResult<()> {
        self.do_update_router_metrics(lifecycle_inc, thegent_inc, changes_inc, hysteresis_inc)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn get_router_metrics(&self, py: Python<'_>) -> PyResult<PyObject> {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        let metrics: &RouterMetricsState =
            unsafe { &*(self.mmap[start..end].as_ptr() as *const RouterMetricsState) };
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_decisions", metrics.total_decisions)?;
        dict.set_item("lifecycle_count", metrics.lifecycle_count)?;
        dict.set_item("thegent_count", metrics.thegent_count)?;
        dict.set_item("route_changes", metrics.route_changes)?;
        dict.set_item("hysteresis_activations", metrics.hysteresis_activations)?;
        Ok(dict.into_any().unbind())
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn py_init_shm(path: Option<String>) -> PyResult<()> {
    let path = path.unwrap_or_else(|| "state.shm".to_string());
    init_global_shm(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_update_provider(
    name: String,
    request_count: u64,
    success_count: u64,
    latency_ms: u32,
) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface
            .do_update_provider(name, request_count, success_count, latency_ms)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_get_provider_metrics(py: Python<'_>, name: String) -> PyResult<Option<PyObject>> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        let mut name_bytes = [0u8; 32];
        let len = name.len().min(32);
        name_bytes[..len].copy_from_slice(&name.as_bytes()[..len]);
        for i in 0..MAX_PROVIDERS {
            let start = PROVIDER_OFFSET + (i * PROVIDER_SLOT_SIZE);
            let slot = &interface.mmap[start..start + 32];
            if *slot == name_bytes {
                let end = start + std::mem::size_of::<ProviderState>();
                let state: &ProviderState =
                    unsafe { &*(interface.mmap[start..end].as_ptr() as *const ProviderState) };
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("request_count", state.request_count)?;
                dict.set_item("success_count", state.success_count)?;
                dict.set_item("latency_ms", state.latency_p50_ms)?;
                dict.set_item("success_rate", state.success_rate)?;
                dict.set_item("last_updated", state.last_updated)?;
                return Ok(Some(dict.into_any().unbind()));
            }
        }
        Ok(None)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_record_failure(target: String, category: i32) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface
            .do_record_failure(target, category)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_award_xp(amount: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface
            .do_award_xp(amount)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_get_xp_state(py: Python<'_>) -> PyResult<Option<PyObject>> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        let state = interface.get_xp_state_internal();
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_xp", state.total_xp)?;
        dict.set_item("level", state.level)?;
        Ok(Some(dict.into_any().unbind()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_set_health_score(score: f64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface
            .do_set_health_score(score)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_get_health_score() -> PyResult<f64> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        Ok(interface.do_get_health_score())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_record_resource_usage(pid: u32, cpu_usage: f32, memory_kb: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface
            .do_record_resource_usage(pid, cpu_usage, memory_kb)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_update_router_metrics(
    lifecycle_inc: u64,
    thegent_inc: u64,
    changes_inc: u64,
    hysteresis_inc: u64,
) -> PyResult<()> {
    update_router_metrics(lifecycle_inc, thegent_inc, changes_inc, hysteresis_inc)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyfunction]
fn py_get_router_metrics(py: Python<'_>) -> PyResult<PyObject> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        let metrics: &RouterMetricsState =
            unsafe { &*(interface.mmap[start..end].as_ptr() as *const RouterMetricsState) };
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_decisions", metrics.total_decisions)?;
        dict.set_item("lifecycle_count", metrics.lifecycle_count)?;
        dict.set_item("thegent_count", metrics.thegent_count)?;
        dict.set_item("route_changes", metrics.route_changes)?;
        dict.set_item("hysteresis_activations", metrics.hysteresis_activations)?;
        Ok(dict.into_any().unbind())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "SHM not initialized",
        ))
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pymodule]
fn thegent_shm(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SHMInterface>()?;
    m.add_function(wrap_pyfunction!(py_init_shm, m)?)?;
    m.add_function(wrap_pyfunction!(py_update_provider, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_provider_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(py_record_failure, m)?)?;
    m.add_function(wrap_pyfunction!(py_award_xp, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_xp_state, m)?)?;
    m.add_function(wrap_pyfunction!(py_set_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(py_record_resource_usage, m)?)?;
    m.add_function(wrap_pyfunction!(py_update_router_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_router_metrics, m)?)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    /// Helper to create a temporary SHM file for testing
    fn create_test_shm() -> (SHMInterface, NamedTempFile) {
        let temp_file = NamedTempFile::new().expect("create temp file");
        let shm = SHMInterface::open(temp_file.path()).expect("open shm");
        (shm, temp_file)
    }

    // ========================================================================
    // Race Track Tests
    // ========================================================================

    #[test]
    fn test_record_race_result() {
        let (mut shm, _temp) = create_test_shm();

        let result = shm.do_record_race_result(
            "race-001",
            "agent-alpha",
            "run-12345",
            "completed",
            1500,
            0.95,
        );

        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 0); // First slot
    }

    #[test]
    fn test_get_race_result() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_record_race_result(
            "race-001",
            "agent-alpha",
            "run-12345",
            "completed",
            1500,
            0.95,
        )
        .unwrap();

        let result = shm.do_get_race_result(0);
        assert!(result.is_some());

        let race = result.unwrap();
        assert!(race.race_id.starts_with(b"race-001"));
        assert!(race.agent_id.starts_with(b"agent-alpha"));
        assert_eq!(race.duration_ms, 1500);
        assert!((race.score - 0.95).abs() < 0.001);
    }

    #[test]
    fn test_get_race_result_empty_slot() {
        let (shm, _temp) = create_test_shm();

        let result = shm.do_get_race_result(0);
        assert!(result.is_none());
    }

    #[test]
    fn test_find_race_result() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_record_race_result(
            "race-find-test",
            "agent-beta",
            "run-99999",
            "running",
            500,
            0.0,
        )
        .unwrap();

        let found = shm.do_find_race_result("race-find-test");
        assert!(found.is_some());

        let (idx, race) = found.unwrap();
        assert_eq!(idx, 0);
        assert!(race.run_id.starts_with(b"run-99999"));
    }

    #[test]
    fn test_find_race_result_not_found() {
        let (shm, _temp) = create_test_shm();

        let found = shm.do_find_race_result("nonexistent");
        assert!(found.is_none());
    }

    #[test]
    fn test_list_race_results() {
        let (mut shm, _temp) = create_test_shm();

        // Record multiple races
        shm.do_record_race_result("race-a", "agent-1", "run-1", "completed", 100, 0.9)
            .unwrap();
        shm.do_record_race_result("race-b", "agent-2", "run-2", "failed", 200, 0.0)
            .unwrap();
        shm.do_record_race_result("race-c", "agent-3", "run-3", "completed", 300, 0.85)
            .unwrap();

        let results = shm.do_list_race_results();
        assert_eq!(results.len(), 3);
    }

    #[test]
    fn test_list_race_results_empty() {
        let (shm, _temp) = create_test_shm();

        let results = shm.do_list_race_results();
        assert!(results.is_empty());
    }

    #[test]
    fn test_clear_race_result() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_record_race_result("race-to-clear", "agent-x", "run-x", "done", 100, 1.0)
            .unwrap();

        let clear_result = shm.do_clear_race_result(0);
        assert!(clear_result.is_ok());

        let result = shm.do_get_race_result(0);
        assert!(result.is_none());
    }

    #[test]
    fn test_clear_race_result_invalid_index() {
        let (mut shm, _temp) = create_test_shm();

        let result = shm.do_clear_race_result(RACE_COUNT + 10);
        assert!(result.is_err());
    }

    #[test]
    fn test_update_existing_race_result() {
        let (mut shm, _temp) = create_test_shm();

        // Record initial result
        shm.do_record_race_result("race-update", "agent-1", "run-1", "running", 0, 0.0)
            .unwrap();

        // Update same race
        shm.do_record_race_result("race-update", "agent-1", "run-1", "completed", 1000, 0.99)
            .unwrap();

        let results = shm.do_list_race_results();
        assert_eq!(results.len(), 1); // Should still be just one result

        let race = shm.do_get_race_result(0).unwrap();
        assert_eq!(race.duration_ms, 1000);
    }

    // ========================================================================
    // Command Cache Tests
    // ========================================================================

    #[test]
    fn test_acquire_command_lock() {
        let (mut shm, _temp) = create_test_shm();

        let result = shm.do_acquire_command_lock("cmd-hash-123", 1001);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 0); // First slot
    }

    #[test]
    fn test_get_command_lock() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("cmd-test-lock", 2001).unwrap();

        let lock = shm.do_get_command_lock("cmd-test-lock");
        assert!(lock.is_some());

        let lock = lock.unwrap();
        assert_eq!(lock.pid, 2001);
        assert!(lock.cmd_hash.starts_with(b"cmd-test-lock"));
    }

    #[test]
    fn test_get_command_lock_not_found() {
        let (shm, _temp) = create_test_shm();

        let lock = shm.do_get_command_lock("nonexistent");
        assert!(lock.is_none());
    }

    #[test]
    fn test_release_command_lock() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("cmd-to-release", 3001).unwrap();

        let release_result = shm.do_release_command_lock("cmd-to-release", 3001);
        assert!(release_result.is_ok());

        let lock = shm.do_get_command_lock("cmd-to-release");
        assert!(lock.is_none());
    }

    #[test]
    fn test_release_command_lock_wrong_pid() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("cmd-wrong-pid", 4001).unwrap();

        // Try to release with different PID
        let result = shm.do_release_command_lock("cmd-wrong-pid", 9999);
        assert!(result.is_err());
        assert_eq!(
            result.unwrap_err().kind(),
            std::io::ErrorKind::PermissionDenied
        );

        // Lock should still exist
        let lock = shm.do_get_command_lock("cmd-wrong-pid");
        assert!(lock.is_some());
    }

    #[test]
    fn test_release_command_lock_not_found() {
        let (mut shm, _temp) = create_test_shm();

        let result = shm.do_release_command_lock("nonexistent", 1001);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().kind(), std::io::ErrorKind::NotFound);
    }

    #[test]
    fn test_update_command_lock() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("cmd-to-update", 5001).unwrap();

        let update_result =
            shm.do_update_command_lock("cmd-to-update", 5001, "completed", "/tmp/output.txt");
        assert!(update_result.is_ok());

        let lock = shm.do_get_command_lock("cmd-to-update").unwrap();
        assert!(lock.status.starts_with(b"completed"));
        assert!(lock.output_path.starts_with(b"/tmp/output.txt"));
    }

    #[test]
    fn test_update_command_lock_wrong_pid() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("cmd-update-wrong", 6001)
            .unwrap();

        let result = shm.do_update_command_lock("cmd-update-wrong", 9999, "failed", "/dev/null");
        assert!(result.is_err());
        assert_eq!(
            result.unwrap_err().kind(),
            std::io::ErrorKind::PermissionDenied
        );
    }

    #[test]
    fn test_list_command_locks() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_acquire_command_lock("lock-a", 101).unwrap();
        shm.do_acquire_command_lock("lock-b", 102).unwrap();
        shm.do_acquire_command_lock("lock-c", 103).unwrap();

        let locks = shm.do_list_command_locks();
        assert_eq!(locks.len(), 3);
    }

    #[test]
    fn test_list_command_locks_empty() {
        let (shm, _temp) = create_test_shm();

        let locks = shm.do_list_command_locks();
        assert!(locks.is_empty());
    }

    #[test]
    fn test_acquire_already_locked_command() {
        let (mut shm, _temp) = create_test_shm();

        // Acquire lock with PID 7001
        shm.do_acquire_command_lock("already-locked", 7001).unwrap();

        // Try to acquire same command with different PID
        let result = shm.do_acquire_command_lock("already-locked", 7002);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().kind(), std::io::ErrorKind::ResourceBusy);
    }

    #[test]
    fn test_reacquire_same_pid() {
        let (mut shm, _temp) = create_test_shm();

        // Acquire lock
        shm.do_acquire_command_lock("reacquire-test", 8001).unwrap();

        // Same PID should be able to re-acquire
        let result = shm.do_acquire_command_lock("reacquire-test", 8001);
        assert!(result.is_ok());
    }

    // ========================================================================
    // Existing SHM functionality tests
    // ========================================================================

    #[test]
    fn test_xp_operations() {
        let (mut shm, _temp) = create_test_shm();

        let initial = shm.do_get_xp_state();
        assert_eq!(initial.level, 1); // Default level

        shm.do_award_xp(500).unwrap();
        let after_award = shm.do_get_xp_state();
        assert_eq!(after_award.total_xp, 500);
        assert_eq!(after_award.level, 1);

        shm.do_award_xp(500).unwrap();
        let level_up = shm.do_get_xp_state();
        assert_eq!(level_up.total_xp, 1000);
        assert_eq!(level_up.level, 2);
    }

    #[test]
    fn test_health_score() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_set_health_score(0.85).unwrap();
        let score = shm.do_get_health_score();
        assert!((score - 0.85).abs() < 0.001);
    }

    #[test]
    fn test_provider_metrics() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_update_provider("openai".to_string(), 100, 95, 150)
            .unwrap();

        let metrics = shm.do_get_provider_metrics("openai");
        assert!(metrics.is_some());

        let provider = metrics.unwrap();
        assert_eq!(provider.request_count, 100);
        assert_eq!(provider.success_count, 95);
        assert_eq!(provider.failure_count, 5);
        assert_eq!(provider.latency_p50_ms, 150);
        assert!((provider.success_rate - 0.95).abs() < 0.001);
    }

    #[test]
    fn test_router_metrics() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_update_router_metrics(5, 10, 2, 1).unwrap();

        let metrics = shm.do_get_router_metrics();
        assert_eq!(metrics.total_decisions, 15);
        assert_eq!(metrics.lifecycle_count, 5);
        assert_eq!(metrics.thegent_count, 10);
        assert_eq!(metrics.route_changes, 2);
        assert_eq!(metrics.hysteresis_activations, 1);
    }

    // ========================================================================
    // CIRCUIT BREAKER TESTS
    // ========================================================================

    #[test]
    fn test_circuit_breaker_records_initial_failure() {
        let (mut shm, _temp) = create_test_shm();

        let result = shm.do_record_failure("service-a".to_string(), 1);
        assert!(result.is_ok());

        // Read back the breaker state to verify it was recorded
        let start = BREAKER_OFFSET;
        let end = start + std::mem::size_of::<BreakerState>();
        let slot = &shm.mmap[start..end];
        let state: &BreakerState = unsafe { &*(slot.as_ptr() as *const BreakerState) };

        assert_eq!(state.failures, 1);
        assert!(state.target.starts_with(b"service-a"));
        assert_eq!(state.category, 1);
    }

    #[test]
    fn test_circuit_breaker_accumulates_failures() {
        let (mut shm, _temp) = create_test_shm();

        // Record multiple failures for same target
        shm.do_record_failure("service-b".to_string(), 1).unwrap();
        shm.do_record_failure("service-b".to_string(), 1).unwrap();
        shm.do_record_failure("service-b".to_string(), 1).unwrap();

        // Read back the breaker state
        let start = BREAKER_OFFSET;
        let end = start + std::mem::size_of::<BreakerState>();
        let slot = &shm.mmap[start..end];
        let state: &BreakerState = unsafe { &*(slot.as_ptr() as *const BreakerState) };

        assert_eq!(state.failures, 3);
    }

    #[test]
    fn test_circuit_breaker_differentiates_by_category() {
        let (mut shm, _temp) = create_test_shm();

        // Record failures for same target but different categories
        shm.do_record_failure("service-c".to_string(), 1).unwrap();
        shm.do_record_failure("service-c".to_string(), 2).unwrap();

        // Should occupy two separate slots
        let start1 = BREAKER_OFFSET;
        let end1 = start1 + std::mem::size_of::<BreakerState>();
        let state1: &BreakerState =
            unsafe { &*(shm.mmap[start1..end1].as_ptr() as *const BreakerState) };

        let start2 = BREAKER_OFFSET + SLOT_SIZE;
        let end2 = start2 + std::mem::size_of::<BreakerState>();
        let state2: &BreakerState =
            unsafe { &*(shm.mmap[start2..end2].as_ptr() as *const BreakerState) };

        assert_eq!(state1.category, 1);
        assert_eq!(state2.category, 2);
    }

    #[test]
    fn test_circuit_breaker_updates_last_failure_timestamp() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_record_failure("service-d".to_string(), 1).unwrap();

        let start = BREAKER_OFFSET;
        let end = start + std::mem::size_of::<BreakerState>();
        let state1: BreakerState =
            unsafe { *(shm.mmap[start..end].as_ptr() as *const BreakerState) };
        let timestamp1 = state1.last_failure;

        std::thread::sleep(std::time::Duration::from_millis(10));

        shm.do_record_failure("service-d".to_string(), 1).unwrap();
        let state2: BreakerState =
            unsafe { *(shm.mmap[start..end].as_ptr() as *const BreakerState) };
        let timestamp2 = state2.last_failure;

        assert!(timestamp2 > timestamp1);
    }

    #[test]
    fn test_circuit_breaker_slots_limited() {
        let (mut shm, _temp) = create_test_shm();

        // Fill up all breaker slots
        for i in 0..MAX_BREAKERS {
            let target = format!("service-{}", i);
            let result = shm.do_record_failure(target, 1);
            assert!(result.is_ok());
        }

        // Next failure should fail (slots full)
        let result = shm.do_record_failure("service-overflow".to_string(), 1);
        assert!(result.is_err());
    }

    #[test]
    fn test_circuit_breaker_reuses_existing_slot() {
        let (mut shm, _temp) = create_test_shm();

        // Record first failure
        shm.do_record_failure("service-e".to_string(), 1).unwrap();

        let start = BREAKER_OFFSET;
        let end = start + std::mem::size_of::<BreakerState>();
        let state1: BreakerState =
            unsafe { *(shm.mmap[start..end].as_ptr() as *const BreakerState) };
        assert_eq!(state1.failures, 1);

        // Record same failure again - should reuse slot, not fill next one
        shm.do_record_failure("service-e".to_string(), 1).unwrap();
        let state2: BreakerState =
            unsafe { *(shm.mmap[start..end].as_ptr() as *const BreakerState) };
        assert_eq!(state2.failures, 2);

        // Next slot should be empty
        let start2 = BREAKER_OFFSET + SLOT_SIZE;
        let end2 = start2 + std::mem::size_of::<BreakerState>();
        let state3: BreakerState =
            unsafe { *(shm.mmap[start2..end2].as_ptr() as *const BreakerState) };
        assert_eq!(state3.failures, 0);
    }

    // ========================================================================
    // THREAD SAFETY TESTS
    // ========================================================================

    #[test]
    fn test_concurrent_reads_consistent() {
        let (mut shm, _temp) = create_test_shm();

        // Set initial state
        shm.do_award_xp(100).unwrap();
        let expected_xp = shm.do_get_xp_state().total_xp;

        let mmap_path = _temp.path().to_path_buf();
        let handles: Vec<_> = (0..4)
            .map(|_| {
                let path = mmap_path.clone();
                std::thread::spawn(move || {
                    let shm = SHMInterface::open(&path).expect("open shm");
                    let xp = shm.do_get_xp_state();
                    xp.total_xp
                })
            })
            .collect();

        // All threads should read the same value
        for handle in handles {
            let xp = handle.join().unwrap();
            assert_eq!(xp, expected_xp);
        }
    }

    #[test]
    fn test_concurrent_writes_not_lost() {
        let (_, _temp) = create_test_shm();
        let mmap_path = _temp.path().to_path_buf();

        let handles: Vec<_> = (0..4)
            .map(|_| {
                let path = mmap_path.clone();
                std::thread::spawn(move || {
                    let mut shm = SHMInterface::open(&path).expect("open shm");
                    shm.do_award_xp(25).expect("award xp");
                })
            })
            .collect();

        for handle in handles {
            handle.join().unwrap();
        }

        // Total should be 4 * 25 = 100
        let shm = SHMInterface::open(&mmap_path).expect("open shm");
        let final_xp = shm.do_get_xp_state().total_xp;
        assert_eq!(final_xp, 100);
    }

    #[test]
    fn test_concurrent_provider_updates() {
        let (_, _temp) = create_test_shm();
        let mmap_path = _temp.path().to_path_buf();

        let handles: Vec<_> = (0..3)
            .map(|i| {
                let path = mmap_path.clone();
                std::thread::spawn(move || {
                    let mut shm = SHMInterface::open(&path).expect("open shm");
                    let provider = format!("provider-{}", i);
                    shm.do_update_provider(provider, 100 + i as u64, 90 + i as u64, 50)
                        .expect("update provider");
                })
            })
            .collect();

        for handle in handles {
            handle.join().unwrap();
        }

        // All providers should be recorded
        let shm = SHMInterface::open(&mmap_path).expect("open shm");
        for i in 0..3 {
            let provider = format!("provider-{}", i);
            let metrics = shm.do_get_provider_metrics(&provider);
            assert!(metrics.is_some());
            assert_eq!(metrics.unwrap().request_count, 100 + i as u64);
        }
    }

    #[test]
    fn test_concurrent_command_lock_acquire_release() {
        let (_, _temp) = create_test_shm();
        let mmap_path = _temp.path().to_path_buf();

        let handles: Vec<_> = (0..4)
            .map(|i| {
                let path = mmap_path.clone();
                std::thread::spawn(move || {
                    // Give each thread time to avoid race conditions
                    std::thread::sleep(std::time::Duration::from_millis(i as u64 * 2));

                    let mut shm = SHMInterface::open(&path).expect("open shm");
                    let cmd_hash = format!("cmd-{}", i);
                    let pid = 1000 + i as u32;

                    let idx = shm
                        .do_acquire_command_lock(&cmd_hash, pid)
                        .expect("acquire lock");
                    assert!(idx < CMD_CACHE_COUNT);

                    // Simulate some work
                    std::thread::sleep(std::time::Duration::from_millis(10));

                    shm.do_release_command_lock(&cmd_hash, pid)
                        .expect("release lock");
                })
            })
            .collect();

        for handle in handles {
            handle.join().unwrap();
        }

        // All locks should be released
        std::thread::sleep(std::time::Duration::from_millis(50));
        let shm = SHMInterface::open(&mmap_path).expect("open shm");
        let locks = shm.do_list_command_locks();
        assert!(locks.is_empty());
    }

    #[test]
    fn test_concurrent_health_score_updates() {
        let (mut shm, _temp) = create_test_shm();
        let mmap_path = _temp.path().to_path_buf();

        // Set initial health
        shm.do_set_health_score(0.5).unwrap();

        let handles: Vec<_> = (0..4)
            .map(|i| {
                let path = mmap_path.clone();
                std::thread::spawn(move || {
                    let mut shm = SHMInterface::open(&path).expect("open shm");
                    let score = 0.5 + (i as f64 * 0.05);
                    shm.do_set_health_score(score).expect("set health");
                })
            })
            .collect();

        for handle in handles {
            handle.join().unwrap();
        }

        // Health score should be one of the written values
        let shm = SHMInterface::open(&mmap_path).expect("open shm");
        let final_score = shm.do_get_health_score();
        assert!((0.5..=0.65).contains(&final_score));
    }

    // ========================================================================
    // SHM STATE PERSISTENCE TESTS
    // ========================================================================

    #[test]
    fn test_xp_state_persists_across_reopens() {
        let temp_file = tempfile::NamedTempFile::new().expect("create temp file");
        let path = temp_file.path().to_path_buf();

        {
            let mut shm = SHMInterface::open(&path).expect("open shm");
            shm.do_award_xp(500).unwrap();
        }

        {
            let shm = SHMInterface::open(&path).expect("open shm");
            let xp = shm.do_get_xp_state();
            assert_eq!(xp.total_xp, 500);
        }
    }

    #[test]
    fn test_health_score_persists_across_reopens() {
        let temp_file = tempfile::NamedTempFile::new().expect("create temp file");
        let path = temp_file.path().to_path_buf();

        {
            let mut shm = SHMInterface::open(&path).expect("open shm");
            shm.do_set_health_score(0.75).unwrap();
        }

        {
            let shm = SHMInterface::open(&path).expect("open shm");
            let score = shm.do_get_health_score();
            assert!((score - 0.75).abs() < 0.001);
        }
    }

    #[test]
    fn test_provider_metrics_persist_across_reopens() {
        let temp_file = tempfile::NamedTempFile::new().expect("create temp file");
        let path = temp_file.path().to_path_buf();

        {
            let mut shm = SHMInterface::open(&path).expect("open shm");
            shm.do_update_provider("persistent-provider".to_string(), 1000, 950, 120)
                .unwrap();
        }

        {
            let shm = SHMInterface::open(&path).expect("open shm");
            let metrics = shm.do_get_provider_metrics("persistent-provider");
            assert!(metrics.is_some());
            let m = metrics.unwrap();
            assert_eq!(m.request_count, 1000);
            assert_eq!(m.success_count, 950);
        }
    }

    #[test]
    fn test_race_results_persist_across_reopens() {
        let temp_file = tempfile::NamedTempFile::new().expect("create temp file");
        let path = temp_file.path().to_path_buf();

        {
            let mut shm = SHMInterface::open(&path).expect("open shm");
            shm.do_record_race_result("race-persist", "agent-1", "run-1", "completed", 2000, 0.99)
                .unwrap();
        }

        {
            let shm = SHMInterface::open(&path).expect("open shm");
            let (idx, race) = shm.do_find_race_result("race-persist").expect("find race");
            assert_eq!(idx, 0);
            assert_eq!(race.duration_ms, 2000);
            assert!((race.score - 0.99).abs() < 0.001);
        }
    }

    // ========================================================================
    // METRICS CALCULATION TESTS
    // ========================================================================

    #[test]
    fn test_xp_level_calculation() {
        let (mut shm, _temp) = create_test_shm();

        // XP < 1000: level 1
        shm.do_award_xp(500).unwrap();
        let state = shm.do_get_xp_state();
        assert_eq!(state.level, 1);

        // XP = 1000: level 2
        shm.do_award_xp(500).unwrap();
        let state = shm.do_get_xp_state();
        assert_eq!(state.level, 2);
        assert_eq!(state.total_xp, 1000);

        // XP = 2000: level 3
        shm.do_award_xp(1000).unwrap();
        let state = shm.do_get_xp_state();
        assert_eq!(state.level, 3);
        assert_eq!(state.total_xp, 2000);
    }

    #[test]
    fn test_provider_success_rate_calculation() {
        let (mut shm, _temp) = create_test_shm();

        // 100 requests, 80 successes = 0.8 success rate
        shm.do_update_provider("calc-test".to_string(), 100, 80, 100)
            .unwrap();

        let metrics = shm.do_get_provider_metrics("calc-test").unwrap();
        assert!((metrics.success_rate - 0.8).abs() < 0.001);
        assert_eq!(metrics.failure_count, 20);
    }

    #[test]
    fn test_provider_success_rate_perfect() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_update_provider("perfect-provider".to_string(), 50, 50, 50)
            .unwrap();

        let metrics = shm.do_get_provider_metrics("perfect-provider").unwrap();
        assert!((metrics.success_rate - 1.0).abs() < 0.001);
    }

    #[test]
    fn test_provider_zero_requests() {
        let (mut shm, _temp) = create_test_shm();

        // 0 requests: success rate should default to 1.0
        shm.do_update_provider("zero-requests".to_string(), 0, 0, 0)
            .unwrap();

        let metrics = shm.do_get_provider_metrics("zero-requests").unwrap();
        assert!((metrics.success_rate - 1.0).abs() < 0.001);
    }

    #[test]
    fn test_router_metrics_cumulative() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_update_router_metrics(10, 20, 5, 2).unwrap();
        let metrics1 = shm.do_get_router_metrics();
        assert_eq!(metrics1.total_decisions, 30);
        assert_eq!(metrics1.lifecycle_count, 10);
        assert_eq!(metrics1.thegent_count, 20);

        shm.do_update_router_metrics(5, 10, 3, 1).unwrap();
        let metrics2 = shm.do_get_router_metrics();
        assert_eq!(metrics2.total_decisions, 45); // 30 + 5 + 10
        assert_eq!(metrics2.lifecycle_count, 15);
        assert_eq!(metrics2.thegent_count, 30);
    }

    // ========================================================================
    // EDGE CASES AND DATA CONSISTENCY TESTS
    // ========================================================================

    #[test]
    fn test_write_then_read_consistency() {
        let (mut shm, _temp) = create_test_shm();

        let values: Vec<f64> = vec![0.1, 0.5, 0.99, 1.0, 0.0];
        for &val in &values {
            shm.do_set_health_score(val).unwrap();
            let read_val = shm.do_get_health_score();
            assert!((read_val - val).abs() < 0.001, "Mismatch for value {}", val);
        }
    }

    #[test]
    fn test_multiple_providers_distinct_slots() {
        let (mut shm, _temp) = create_test_shm();

        shm.do_update_provider("p1".to_string(), 100, 90, 50)
            .unwrap();
        shm.do_update_provider("p2".to_string(), 200, 180, 60)
            .unwrap();
        shm.do_update_provider("p3".to_string(), 300, 270, 70)
            .unwrap();

        let m1 = shm.do_get_provider_metrics("p1").unwrap();
        let m2 = shm.do_get_provider_metrics("p2").unwrap();
        let m3 = shm.do_get_provider_metrics("p3").unwrap();

        assert_eq!(m1.request_count, 100);
        assert_eq!(m2.request_count, 200);
        assert_eq!(m3.request_count, 300);
    }

    #[test]
    fn test_empty_slot_detection() {
        let (shm, _temp) = create_test_shm();

        // Fresh SHM should have no XP
        let xp = shm.do_get_xp_state();
        assert_eq!(xp.level, 1);
        assert_eq!(xp.total_xp, 0);
    }

    #[test]
    fn test_command_lock_stress() {
        let (mut shm, _temp) = create_test_shm();

        // Acquire and release many locks
        for i in 0..50 {
            let cmd_hash = format!("cmd-stress-{}", i);
            let idx = shm.do_acquire_command_lock(&cmd_hash, 5000).unwrap();
            assert!(idx < CMD_CACHE_COUNT);

            shm.do_release_command_lock(&cmd_hash, 5000).unwrap();
        }
    }

    #[test]
    fn test_race_result_update_in_place() {
        let (mut shm, _temp) = create_test_shm();

        // Record initial race
        shm.do_record_race_result("race-update-test", "agent-1", "run-1", "running", 100, 0.0)
            .unwrap();

        // Update same race
        shm.do_record_race_result(
            "race-update-test",
            "agent-1",
            "run-1",
            "completed",
            1500,
            0.95,
        )
        .unwrap();

        // Should be exactly 1 result (not 2)
        let results = shm.do_list_race_results();
        assert_eq!(results.len(), 1);

        let (_, race) = results.first().unwrap();
        assert_eq!(race.duration_ms, 1500);
        assert!((race.score - 0.95).abs() < 0.001);
    }

    #[test]
    fn test_arc_shared_shm_across_threads() {
        use std::sync::Arc;

        let temp_file = tempfile::NamedTempFile::new().expect("create temp file");
        let path = Arc::new(temp_file.path().to_path_buf());

        let mut initial_shm = SHMInterface::open(path.as_ref()).expect("open shm");
        initial_shm.do_award_xp(250).unwrap();
        drop(initial_shm);

        let handles: Vec<_> = (0..3)
            .map(|i| {
                let path = Arc::clone(&path);
                std::thread::spawn(move || {
                    let mut shm = SHMInterface::open(path.as_ref()).expect("open shm");
                    shm.do_award_xp(50).expect("award xp");
                    let xp = shm.do_get_xp_state();
                    (i, xp.total_xp)
                })
            })
            .collect();

        let mut total_xp = 250;
        for handle in handles {
            let (_, _xp) = handle.join().unwrap();
            total_xp += 50;
        }

        let final_shm = SHMInterface::open(path.as_ref()).expect("open shm");
        assert_eq!(final_shm.do_get_xp_state().total_xp, total_xp);
    }
}
