#[cfg(feature = "python")]
use pyo3::prelude::*;
use git2::{Repository as Git2Repository, StatusOptions, ObjectType};

#[cfg(feature = "gix")]
pub mod gix_impl {
    // gix implementation is currently broken, using git2 fallback
    pub fn get_head_sha(_path: Option<String>) -> Result<Option<String>, String> {
        Err("gix implementation not available".to_string())
    }

    pub fn get_branch_name(_path: Option<String>) -> Result<Option<String>, String> {
        Err("gix implementation not available".to_string())
    }

    pub fn is_dirty(_path: Option<String>) -> Result<bool, String> {
        Err("gix implementation not available".to_string())
    }
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_head_sha(path: Option<String>) -> PyResult<Option<String>> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let head = repo.head().ok();
    if let Some(h) = head {
        if let Some(target) = h.target() {
            return Ok(Some(target.to_string()));
        }
    }
    Ok(None)
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_branch_name(path: Option<String>) -> PyResult<Option<String>> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let head = repo.head().ok();
    if let Some(h) = head {
        if let Some(name) = h.shorthand() {
            return Ok(Some(name.to_string()));
        }
    }
    Ok(None)
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn is_dirty(path: Option<String>) -> PyResult<bool> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let mut options = StatusOptions::new();
    options.include_untracked(true).recurse_untracked_dirs(true);
    let statuses = repo.statuses(Some(&mut options)).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    Ok(!statuses.is_empty())
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_status_short(path: Option<String>) -> PyResult<String> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let mut options = StatusOptions::new();
    options.include_untracked(true).recurse_untracked_dirs(true);
    let statuses = repo.statuses(Some(&mut options)).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let mut out = String::new();
    for entry in statuses.iter() {
        let status = entry.status();
        let code = if status.is_index_new() || status.is_wt_new() { "A" }
                  else if status.is_index_modified() || status.is_wt_modified() { "M" }
                  else if status.is_index_deleted() || status.is_wt_deleted() { "D" }
                  else if status.is_index_renamed() || status.is_wt_renamed() { "R" }
                  else { "?" };
        if let Some(p) = entry.path() {
            out.push_str(&format!("{} {}\n", code, p));
        }
    }
    Ok(out)
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None, base=None))]
fn get_diff(path: Option<String>, base: Option<String>) -> PyResult<String> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let diff = if let Some(base_ref) = base {
        let obj = repo.revparse_single(&base_ref).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let tree = obj.peel_to_tree().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        repo.diff_tree_to_workdir_with_index(Some(&tree), None).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
    } else {
        match repo.head() {
            Ok(head) => {
                let obj = head.peel(ObjectType::Tree).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                let tree = obj.as_tree().unwrap();
                repo.diff_tree_to_workdir_with_index(Some(tree), None).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
            },
            Err(_) => {
                repo.diff_tree_to_workdir_with_index(None, None).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
            }
        }
    };

    let mut output = String::new();
    diff.print(git2::DiffFormat::Patch, |_delta, _hunk, line| {
        output.push(line.origin());
        if let Ok(s) = std::str::from_utf8(line.content()) {
            output.push_str(s);
        }
        true
    }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    Ok(output)
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_diff_stats(path: Option<String>) -> PyResult<PyObject> {
    let path = path.unwrap_or_else(|| ".".to_string());
    let repo = Git2Repository::discover(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let diff = match repo.head() {
        Ok(head) => {
            let obj = head.peel(ObjectType::Tree).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
            let tree = obj.as_tree().unwrap();
            repo.diff_tree_to_workdir_with_index(Some(tree), None).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
        },
        Err(_) => {
            repo.diff_tree_to_workdir_with_index(None, None).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
        }
    };

    let stats = diff.stats().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    Python::with_gil(|py| {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("files_changed", stats.files_changed())?;
        dict.set_item("insertions", stats.insertions())?;
        dict.set_item("deletions", stats.deletions())?;
        Ok(dict.into())
    })
}

#[cfg(feature = "python")]
#[pymodule]
fn thegent_git(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_head_sha, m)?)?;
    m.add_function(wrap_pyfunction!(get_branch_name, m)?)?;
    m.add_function(wrap_pyfunction!(is_dirty, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_short, m)?)?;
    m.add_function(wrap_pyfunction!(get_diff, m)?)?;
    m.add_function(wrap_pyfunction!(get_diff_stats, m)?)?;
    Ok(())
}
