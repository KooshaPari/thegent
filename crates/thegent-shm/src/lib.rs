use pyo3::prelude::*;
use std::sync::Mutex;
use memmap2::MmapMut;
use std::fs::OpenOptions;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};
use once_cell::sync::Lazy;

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
struct ProviderState {
    name: [u8; 32],
    request_count: u64,
    success_count: u64,
    failure_count: u64,
    latency_p50_ms: u32,
    success_rate: f32,
    last_updated: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct XPState {
    total_xp: u64,
    level: u32,
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
struct RaceResult {
    race_id: [u8; 64],
    agent_id: [u8; 64],
    run_id: [u8; 64],
    status: [u8; 16],
    duration_ms: u64,
    score: f32,
    timestamp: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct CommandLock {
    cmd_hash: [u8; 64],
    pid: u32,
    status: [u8; 16],
    output_path: [u8; 256],
    start_time: f64,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct RouterMetricsState {
    total_decisions: u64,
    lifecycle_count: u64,
    thegent_count: u64,
    route_changes: u64,
    hysteresis_activations: u64,
}

#[pyclass]
pub struct SHMInterface {
    mmap: MmapMut,
}

#[pymethods]
impl SHMInterface {
    #[new]
    #[pyo3(signature = (path))]
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

    fn update_provider(&mut self, name: String, request_count: u64, success_count: u64, latency_ms: u32) -> PyResult<()> {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64();
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
                if target_idx.is_none() { target_idx = Some(i); }
                continue;
            }
            if slot == &name_bytes {
                target_idx = Some(i);
                break;
            }
        }

        let idx = target_idx.ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Provider slots full"))?;
        let start = PROVIDER_OFFSET + (idx * PROVIDER_SLOT_SIZE);
        let end = start + std::mem::size_of::<ProviderState>();
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                (&new_state as *const ProviderState) as *const u8,
                std::mem::size_of::<ProviderState>()
            )
        };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    fn get_provider_metrics(&self, py: Python<'_>, name: String) -> PyResult<Option<PyObject>> {
        let mut name_bytes = [0u8; 32];
        let len = name.len().min(32);
        name_bytes[..len].copy_from_slice(&name.as_bytes()[..len]);

        for i in 0..MAX_PROVIDERS {
            let start = PROVIDER_OFFSET + (i * PROVIDER_SLOT_SIZE);
            let slot = &self.mmap[start..start + 32];
            if slot == &name_bytes {
                let end = start + std::mem::size_of::<ProviderState>();
                let state: &ProviderState = unsafe { &*(self.mmap[start..end].as_ptr() as *const ProviderState) };
                
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

    // ... (rest of existing methods adapted to new offsets) ...
    fn record_failure(&mut self, target: String, category: i32) -> PyResult<()> {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64();
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
                if first_empty.is_none() { first_empty = Some(i); }
                continue;
            }
            if state.target == target_fixed && state.category == category {
                found_idx = Some((i, *state));
                break;
            }
        }

        let (idx, mut state) = if let Some((i, s)) = found_idx { (i, s) } 
                               else if let Some(i) = first_empty { (i, BreakerState { target: target_fixed, category, failures: 0, last_failure: 0.0 }) }
                               else { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM Breaker slots full")); };

        state.failures += 1;
        state.last_failure = now;
        let start = BREAKER_OFFSET + (idx * SLOT_SIZE);
        let end = start + std::mem::size_of::<BreakerState>();
        let bytes: &[u8] = unsafe { std::slice::from_raw_parts((&state as *const BreakerState) as *const u8, std::mem::size_of::<BreakerState>()) };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    fn award_xp(&mut self, amount: u64) -> PyResult<()> {
        let mut state = self.get_xp_state_internal();
        state.total_xp += amount;
        state.level = (state.total_xp / 1000) as u32 + 1;
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
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64();
        let state = ResourceMetrics { pid, cpu_usage, memory_kb, timestamp: now };
        let start = RESOURCE_OFFSET;
        let end = RESOURCE_OFFSET + std::mem::size_of::<ResourceMetrics>();
        let bytes: &[u8] = unsafe { std::slice::from_raw_parts((&state as *const ResourceMetrics) as *const u8, std::mem::size_of::<ResourceMetrics>()) };
        self.mmap[start..end].copy_from_slice(bytes);
        Ok(())
    }

    fn update_router_metrics(&mut self, lifecycle_inc: u64, thegent_inc: u64, changes_inc: u64, hysteresis_inc: u64) -> PyResult<()> {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        let metrics: &mut RouterMetricsState = unsafe { &mut *(self.mmap[start..end].as_ptr() as *mut RouterMetricsState) };
        metrics.total_decisions += lifecycle_inc + thegent_inc;
        metrics.lifecycle_count += lifecycle_inc;
        metrics.thegent_count += thegent_inc;
        metrics.route_changes += changes_inc;
        metrics.hysteresis_activations += hysteresis_inc;
        Ok(())
    }

    fn get_router_metrics(&self, py: Python<'_>) -> PyResult<PyObject> {
        let start = ROUTER_METRICS_OFFSET;
        let end = start + std::mem::size_of::<RouterMetricsState>();
        let metrics: &RouterMetricsState = unsafe { &*(self.mmap[start..end].as_ptr() as *const RouterMetricsState) };
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("total_decisions", metrics.total_decisions)?;
        dict.set_item("lifecycle_count", metrics.lifecycle_count)?;
        dict.set_item("thegent_count", metrics.thegent_count)?;
        dict.set_item("route_changes", metrics.route_changes)?;
        dict.set_item("hysteresis_activations", metrics.hysteresis_activations)?;
        Ok(dict.into_any().unbind())
    }
}

impl SHMInterface {
    fn get_xp_state_internal(&self) -> XPState {
        let start = XP_OFFSET;
        let end = start + std::mem::size_of::<XPState>();
        let slot = &self.mmap[start..end];
        let state: &XPState = unsafe { &*(slot.as_ptr() as *const XPState) };
        if state.level == 0 { return XPState { total_xp: 0, level: 1 }; }
        *state
    }

    fn save_xp_state(&mut self, state: XPState) -> PyResult<()> {
        let start = XP_OFFSET;
        let end = start + std::mem::size_of::<XPState>();
        let bytes: &[u8] = unsafe { std::slice::from_raw_parts((&state as *const XPState) as *const u8, std::mem::size_of::<XPState>()) };
        self.mmap[start..end].copy_from_slice(bytes);
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
fn update_provider(name: String, request_count: u64, success_count: u64, latency_ms: u32) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.update_provider(name, request_count, success_count, latency_ms)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn get_provider_metrics(py: Python<'_>, name: String) -> PyResult<Option<PyObject>> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        interface.get_provider_metrics(py, name)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn record_failure(target: String, category: i32) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.record_failure(target, category)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn award_xp(amount: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.award_xp(amount)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn get_xp_state(py: Python<'_>) -> PyResult<Option<PyObject>> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        interface.get_xp_state(py)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn set_health_score(score: f64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.set_health_score(score)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn get_health_score() -> PyResult<f64> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        interface.get_health_score()
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn record_resource_usage(pid: u32, cpu_usage: f32, memory_kb: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.record_resource_usage(pid, cpu_usage, memory_kb)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn update_router_metrics(lifecycle_inc: u64, thegent_inc: u64, changes_inc: u64, hysteresis_inc: u64) -> PyResult<()> {
    let mut global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_mut() {
        interface.update_router_metrics(lifecycle_inc, thegent_inc, changes_inc, hysteresis_inc)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pyfunction]
fn get_router_metrics(py: Python<'_>) -> PyResult<PyObject> {
    let global = GLOBAL_SHM.lock().unwrap();
    if let Some(interface) = global.as_ref() {
        interface.get_router_metrics(py)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("SHM not initialized"))
    }
}

#[pymodule]
fn thegent_shm(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SHMInterface>()?;
    m.add_function(wrap_pyfunction!(init_shm, m)?)?;
    m.add_function(wrap_pyfunction!(update_provider, m)?)?;
    m.add_function(wrap_pyfunction!(get_provider_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(record_failure, m)?)?;
    m.add_function(wrap_pyfunction!(award_xp, m)?)?;
    m.add_function(wrap_pyfunction!(get_xp_state, m)?)?;
    m.add_function(wrap_pyfunction!(set_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(get_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(record_resource_usage, m)?)?;
    m.add_function(wrap_pyfunction!(update_router_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(get_router_metrics, m)?)?;
    Ok(())
}
