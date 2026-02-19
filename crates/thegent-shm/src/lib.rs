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
const SHM_SIZE: usize = RESOURCE_OFFSET + 1024;

static GLOBAL_SHM: Lazy<Mutex<Option<SHMInterface>>> = Lazy::new(|| Mutex::new(None));

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

    fn get_xp_state(&self) -> PyResult<Option<PyObject>> {
        let state = self.get_xp_state_internal();
        Python::with_gil(|py| {
            let dict = pyo3::types::PyDict::new_bound(py);
            dict.set_item("total_xp", state.total_xp)?;
            dict.set_item("level", state.level)?;
            Ok(Some(dict.into()))
        })
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

    fn get_resource_usage(&self) -> PyResult<Option<PyObject>> {
        let slot = &self.mmap[RESOURCE_OFFSET..RESOURCE_OFFSET+128];
        if slot[0] == 0 { return Ok(None); }
        if let Ok(state) = serde_json::from_slice::<ResourceMetrics>(slot) {
            return Python::with_gil(|py| {
                let dict = pyo3::types::PyDict::new_bound(py);
                dict.set_item("pid", state.pid)?;
                dict.set_item("cpu_usage", state.cpu_usage)?;
                dict.set_item("memory_kb", state.memory_kb)?;
                dict.set_item("timestamp", state.timestamp)?;
                Ok(Some(dict.into()))
            });
        }
        Ok(None)
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

#[pymodule]
fn thegent_shm(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SHMInterface>()?;
    m.add_function(wrap_pyfunction!(init_shm, m)?)?;
    m.add_function(wrap_pyfunction!(set_health_score, m)?)?;
    m.add_function(wrap_pyfunction!(record_resource_usage, m)?)?;
    Ok(())
}
