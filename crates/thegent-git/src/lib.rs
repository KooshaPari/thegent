//! BKM-06: thegent-git - Fast git operations via gix (pure Rust)

use pyo3::prelude::*;

fn open_repo(path: &str) -> Result<gix::Repository, String> {
    gix::discover(path)
        .map_err(|e| format!("not a git repository at {}: {}", path, e))
}

#[pyfunction]
#[pyo3(signature = (path=None))]
pub fn get_head_sha(path: Option<String>) -> PyResult<Option<String>> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = open_repo(&p)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;
    match repo.head_id() {
        Ok(id) => Ok(Some(id.to_hex().to_string())),
        Err(_) => Ok(None),
    }
}

#[pyfunction]
#[pyo3(signature = (path=None))]
pub fn get_branch_name(path: Option<String>) -> PyResult<Option<String>> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = open_repo(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;
    let head = repo.head().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("HEAD error: {}", e)))?;
    Ok(match head.kind {
        gix::head::Kind::Symbolic(r) => Some(r.name.shorten().to_string()),
        _ => None,
    })
}

#[pyfunction]
#[pyo3(signature = (path=None))]
pub fn is_dirty(path: Option<String>) -> PyResult<bool> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = open_repo(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;
    repo.is_dirty()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("dirty check error: {}", e)))
}

#[pyfunction]
#[pyo3(signature = (path=None))]
pub fn get_status(py: Python<'_>, path: Option<String>) -> PyResult<PyObject> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = open_repo(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;
    let branch = repo.head().ok().and_then(|h| match h.kind {
        gix::head::Kind::Symbolic(r) => Some(r.name.shorten().to_string()),
        _ => None,
    });
    let sha = repo.head_id().ok().map(|id| id.to_hex().to_string());
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("branch", branch)?;
    dict.set_item("sha", sha)?;
    dict.set_item("staged", 0u64)?;
    dict.set_item("unstaged", 0u64)?;
    dict.set_item("untracked", 0u64)?;
    Ok(dict.into_any().unbind())
}

#[pymodule]
fn thegent_git(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_head_sha, m)?)?;
    m.add_function(wrap_pyfunction!(get_branch_name, m)?)?;
    m.add_function(wrap_pyfunction!(is_dirty, m)?)?;
    m.add_function(wrap_pyfunction!(get_status, m)?)?;
    Ok(())
}
