use pyo3::prelude::*;
use std::sync::Mutex;
use memmap2::MmapMut;
use std::fs::OpenOptions;
use std::path::PathBuf;
use serde::{Serialize, Deserialize};
use std::time::{SystemTime, UNIX_EPOCH};
use once_cell::sync::Lazy;

const MAX_BREAKERS: usize = 256;
const SLOT_SIZE: usize = 128; 
const XP_OFFSET: usize = MAX_BREAKERS * SLOT_SIZE;
const HEALTH_OFFSET: usize = XP_OFFSET + 64;
const RESOURCE_OFFSET: usize = HEALTH_OFFSET + 64;
const RACE_OFFSET: usize = RESOURCE_OFFSET + 1024;
const RACE_COUNT: usize = 32;
const RACE_SLOT_SIZE: usize = 256;
const CMD_CACHE_OFFSET: usize = RACE_OFFSET + (RACE_COUNT * RACE_SLOT_SIZE);
const CMD_CACHE_COUNT: usize = 64;
const CMD_CACHE_SLOT_SIZE: usize = 512;
const SHM_SIZE: usize = CMD_CACHE_OFFSET + (CMD_CACHE_COUNT * CMD_CACHE_SLOT_SIZE);

static GLOBAL_SHM: Lazy<Mutex<Option<SHMInterface>>> = Lazy::new(|| Mutex::new(None));

#[derive(Serialize, Deserialize, Debug, Clone)]
struct CommandLock {
    cmd_hash: String,
    pid: u32,
    status: String, // "running", "completed", "failed"
    output_path: String,
    start_time: f64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct RaceResult {
    race_id: String,
    agent_id: String,
    run_id: String,
    status: String, // "success", "failed", "running"
    duration_ms: u64,
    score: f32,
    timestamp: f64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct BreakerState {
    target: String,
    category: i32,
    failures: u32,
    last_failure: f64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct XPState {
    total_xp: u64,
    level: u32,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct ResourceMetrics {
    pid: u32,
    cpu_usage: f32,
    memory_kb: u64,
    timestamp: f64,
}

#[pyclass]
struct SHMInterface {
    mmap: MmapMut,
}

#[pymethods]
impl SHMInterface {
    #[new]
    fn new(path: String) -> PyResult<Self> {
        let path = PathBuf::from(path);
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&path)?;
        file.set_len(SHM_SIZE as u64)?;

        let mmap = unsafe { MmapMut::map_mut(&file)? };
        Ok(SHMInterface { mmap })
    }

    fn record_failure(&mut self, target: String, category: i32) -> PyResult<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        
        let mut found_idx = None;
        let mut first_empty = None;

        for i in 0..MAX_BREAKERS {
            let start = i * SLOT_SIZE;
            let end = start + SLOT_SIZE;
            let slot = &self.mmap[start..end];
            if slot[0] == 0 {
                if first_empty.is_none() { first_empty = Some(i); }
                continue;
            }
            if let Ok(state) = serde_json::from_slice::<BreakerState>(&slot[..]) {
                if state.target == target && state.category == category {
                    found_idx = Some((i, state));
                    break;
                }
            }
        }

        let (idx, mut state) = if let Some((i, s)) = found_idx {
            (i, s)
        } else if let Some(i) = first_empty {
            (i, BreakerState { target, category, failures: 0, last_failure: 0.0 })
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM Breaker slots full"));
        };

        state.failures += 1;
        state.last_failure = now;

        let bytes = serde_json::to_vec(&state).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let start = idx * SLOT_SIZE;
        let end = start + SLOT_SIZE;
        for b in &mut self.mmap[start..end] { *b = 0; }
        let len = bytes.len().min(SLOT_SIZE);
        self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
        Ok(())
    }

    fn is_open(&self, target: String, category: i32, threshold: u32, window_s: f64, recovery_s: f64) -> PyResult<bool> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        for i in 0..MAX_BREAKERS {
            let start = i * SLOT_SIZE;
            let end = start + SLOT_SIZE;
            let slot = &self.mmap[start..end];
            if slot[0] == 0 { continue; }
            if let Ok(state) = serde_json::from_slice::<BreakerState>(&slot[..]) {
                if state.target == target && state.category == category {
                    if state.failures >= threshold {
                        if (now - state.last_failure) < window_s {
                            if (now - state.last_failure) > recovery_s {
                                return Ok(false);
                            }
                            return Ok(true);
                        }
                    }
                    return Ok(false);
                }
            }
        }
        Ok(false)
    }

    fn award_xp(&mut self, amount: u64) -> PyResult<()> {
        let mut state = self.get_xp_state_internal();
        state.total_xp += amount;
        state.level = (state.total_xp / 1000) as u32 + 1;
        self.save_xp_state(state)
    }

    fn set_level(&mut self, level: u32) -> PyResult<()> {
        let mut state = self.get_xp_state_internal();
        state.level = level;
        self.save_xp_state(state)
    }

    fn get_xp_state(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let state = self.get_xp_state_internal();
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_xp", state.total_xp)?;
        dict.set_item("level", state.level)?;
        Ok(Some(dict.into_any().unbind()))
    }

    fn set_health_score(&mut self, score: f64) -> PyResult<()> {
        let bytes = score.to_le_bytes();
        self.mmap[HEALTH_OFFSET..HEALTH_OFFSET+8].copy_from_slice(&bytes);
        Ok(())
    }

    fn get_health_score(&self) -> PyResult<f64> {
        let mut bytes = [0u8; 8];
        bytes.copy_from_slice(&self.mmap[HEALTH_OFFSET..HEALTH_OFFSET+8]);
        Ok(f64::from_le_bytes(bytes))
    }

    fn record_resource_usage(&mut self, pid: u32, cpu_usage: f32, memory_kb: u64) -> PyResult<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        let state = ResourceMetrics { pid, cpu_usage, memory_kb, timestamp: now };
        let bytes = serde_json::to_vec(&state).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let start = RESOURCE_OFFSET;
        let end = RESOURCE_OFFSET + 128; // Single slot for current process resource info
        for b in &mut self.mmap[start..end] { *b = 0; }
        let len = bytes.len().min(128);
        self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
        Ok(())
    }

    fn get_resource_usage(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let slot = &self.mmap[RESOURCE_OFFSET..RESOURCE_OFFSET+128];
        if slot[0] == 0 { return Ok(None); }
        if let Ok(state) = serde_json::from_slice::<ResourceMetrics>(slot) {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("pid", state.pid)?;
            dict.set_item("cpu_usage", state.cpu_usage)?;
            dict.set_item("memory_kb", state.memory_kb)?;
            dict.set_item("timestamp", state.timestamp)?;
            Ok(Some(dict.into_any().unbind()))
        } else {
            Ok(None)
        }
    }

    fn record_race_result(&mut self, race_id: String, agent_id: String, run_id: String, status: String, duration_ms: u64, score: f32) -> PyResult<()> {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64();
        let result = RaceResult {
            race_id: race_id.clone(),
            agent_id,
            run_id,
            status,
            duration_ms,
            score,
            timestamp: now,
        };

        let bytes = serde_json::to_vec(&result).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        // Find slot for this race_id or an empty one
        let mut target_idx = None;
        for i in 0..RACE_COUNT {
            let start = RACE_OFFSET + (i * RACE_SLOT_SIZE);
            let slot = &self.mmap[start..start+RACE_SLOT_SIZE];
            if slot[0] == 0 {
                if target_idx.is_none() { target_idx = Some(i); }
                continue;
            }
            if let Ok(existing) = serde_json::from_slice::<RaceResult>(slot) {
                if existing.race_id == race_id && existing.run_id == result.run_id {
                    target_idx = Some(i);
                    break;
                }
            }
        }

        let idx = target_idx.ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Race slots full"))?;
        let start = RACE_OFFSET + (idx * RACE_SLOT_SIZE);
        for b in &mut self.mmap[start..start+RACE_SLOT_SIZE] { *b = 0; }
        let len = bytes.len().min(RACE_SLOT_SIZE);
        self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
        Ok(())
    }

    fn get_race_winner(&self, py: Python<'_>, race_id: String) -> PyResult<Option<PyObject>> {
        let mut best_result: Option<RaceResult> = None;

        for i in 0..RACE_COUNT {
            let start = RACE_OFFSET + (i * RACE_SLOT_SIZE);
            let slot = &self.mmap[start..start+RACE_SLOT_SIZE];
            if slot[0] == 0 { continue; }
            if let Ok(res) = serde_json::from_slice::<RaceResult>(slot) {
                if res.race_id == race_id && res.status == "success" {
                    match &best_result {
                        None => best_result = Some(res),
                        Some(best) => {
                            // Winner is first to finish or highest score? 
                            // For now, let's say first to finish (lowest duration)
                            if res.duration_ms < best.duration_ms {
                                best_result = Some(res);
                            }
                        }
                    }
                }
            }
        }

        if let Some(winner) = best_result {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("agent_id", winner.agent_id)?;
            dict.set_item("run_id", winner.run_id)?;
            dict.set_item("duration_ms", winner.duration_ms)?;
            dict.set_item("score", winner.score)?;
            Ok(Some(dict.into_any().unbind()))
        } else {
            Ok(None)
        }
    }

    fn try_acquire_cmd_lock(&mut self, py: Python<'_>, cmd_hash: String, pid: u32, output_path: String) -> PyResult<Option<PyObject>> {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64();
        
        // 1. Check for existing lock
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start+CMD_CACHE_SLOT_SIZE];
            if slot[0] == 0 { continue; }
            
            if let Ok(lock) = serde_json::from_slice::<CommandLock>(slot) {
                if lock.cmd_hash == cmd_hash {
                    // Lock exists. Is the PID still alive? (In a real system we'd check /proc)
                    // For now, if it's "running", return the existing lock info.
                    if lock.status == "running" {
                        let dict = pyo3::types::PyDict::new(py);
                        dict.set_item("pid", lock.pid)?;
                        dict.set_item("output_path", lock.output_path)?;
                        dict.set_item("start_time", lock.start_time)?;
                        return Ok(Some(dict.into_any().unbind()));
                    }
                }
            }
        }

        // 2. No active lock, create one
        let new_lock = CommandLock {
            cmd_hash: cmd_hash.clone(),
            pid,
            status: "running".to_string(),
            output_path,
            start_time: now,
        };

        let bytes = serde_json::to_vec(&new_lock).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        // Find empty slot
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            if self.mmap[start] == 0 {
                let len = bytes.len().min(CMD_CACHE_SLOT_SIZE);
                self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
                return Ok(None); // Success, lock acquired (None means no existing conflict)
            }
        }

        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Command cache slots full"))
    }

    fn release_cmd_lock(&mut self, cmd_hash: String, status: String) -> PyResult<()> {
        for i in 0..CMD_CACHE_COUNT {
            let start = CMD_CACHE_OFFSET + (i * CMD_CACHE_SLOT_SIZE);
            let slot = &self.mmap[start..start+CMD_CACHE_SLOT_SIZE];
            if slot[0] == 0 { continue; }
            
            if let Ok(mut lock) = serde_json::from_slice::<CommandLock>(slot) {
                if lock.cmd_hash == cmd_hash {
                    lock.status = status;
                    let bytes = serde_json::to_vec(&lock).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                    for b in &mut self.mmap[start..start+CMD_CACHE_SLOT_SIZE] { *b = 0; }
                    let len = bytes.len().min(CMD_CACHE_SLOT_SIZE);
                    self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
                    return Ok(());
                }
            }
        }
        Ok(())
    }
}

impl SHMInterface {
    fn get_xp_state_internal(&self) -> XPState {
        let slot = &self.mmap[XP_OFFSET..XP_OFFSET+64];
        if slot[0] == 0 {
            return XPState { total_xp: 0, level: 1 };
        }
        serde_json::from_slice::<XPState>(slot).unwrap_or(XPState { total_xp: 0, level: 1 })
    }

    fn save_xp_state(&mut self, state: XPState) -> PyResult<()> {
        let bytes = serde_json::to_vec(&state).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let start = XP_OFFSET;
        let end = XP_OFFSET + 64;
        for b in &mut self.mmap[start..end] { *b = 0; }
        let len = bytes.len().min(64);
        self.mmap[start..start+len].copy_from_slice(&bytes[..len]);
        Ok(())
    }
}

#[pyfunction]
#[pyo3(signature = (path=None))]
fn init_shm(path: Option<String>) -> PyResult<()> {
    let path = path.unwrap_or_else(|| "state.shm".to_string());
    let interface = SHMInterface::new(path)?;
    let mut global = GLOBAL_SHM.lock().unwrap();
    *global = Some(interface);
    Ok(())
}

#[pyfunction]
fn set_health_score(score: f64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.set_health_score(score)?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn record_resource_usage(pid: u32, cpu_usage: f32, memory_kb: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.record_resource_usage(pid, cpu_usage, memory_kb)?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn record_race_result(race_id: String, agent_id: String, run_id: String, status: String, duration_ms: u64, score: f32) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.record_race_result(race_id, agent_id, run_id, status, duration_ms, score)?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn get_race_winner(py: Python<'_>, race_id: String) -> PyResult<Option<PyObject>> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.get_race_winner(py, race_id)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn try_acquire_cmd_lock(py: Python<'_>, cmd_hash: String, pid: u32, output_path: String) -> PyResult<Option<PyObject>> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.try_acquire_cmd_lock(py, cmd_hash, pid, output_path)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn release_cmd_lock(cmd_hash: String, status: String) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.release_cmd_lock(cmd_hash, status)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pymodule]
fn thegent_shm(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SHMInterface>()?;
    m.add_function(wrap_pyfunction!(init_shm, m)?)?;
    m.add_function(wrap_pyfunction!(set_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(record_resource_usage, m)?)?;
    m.add_function(wrap_pyfunction!(record_race_result, m)?)?;
    m.add_function(wrap_pyfunction!(get_race_winner, m)?)?;
    m.add_function(wrap_pyfunction!(try_acquire_cmd_lock, m)?)?;
    m.add_function(wrap_pyfunction!(release_cmd_lock, m)?)?;
    Ok(())
}
