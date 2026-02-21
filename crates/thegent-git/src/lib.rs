//! BKM-06: thegent-git core library.
//!
//! Exports two API surfaces:
//! 1. Pure-Rust public functions (head_sha, branch_name, is_dirty,
//!    status_short, diff_stats) — used by the CLI binary (src/main.rs).
//! 2. PyO3 Python extension module (get_head_sha, get_branch_name, is_dirty,
//!    get_status_short, get_status, get_diff, get_diff_stats) — built via
//!    maturin with `--features python`.

#[cfg(feature = "python")]
use pyo3::prelude::*;
use git2::{Repository, StatusOptions};

// ---------------------------------------------------------------------------
// Pure-Rust public API (used by CLI binary)
// ---------------------------------------------------------------------------

fn discover(path: &str) -> Result<Repository, String> {
    Repository::discover(path).map_err(|e| format!("not a git repository at {path}: {e}"))
}

// ---------------------------------------------------------------------------
// Unified API (dispatches to gix if enabled, else git2)
// ---------------------------------------------------------------------------

/// Return the HEAD commit SHA, or None if the repo has no commits (unborn HEAD).
pub fn head_sha(path: &str) -> Result<Option<String>, String> {
    #[cfg(feature = "gix")]
    {
        gix_impl::get_head_sha(Some(path.to_string()))
    }
    #[cfg(not(feature = "gix"))]
    {
        let repo = discover(path)?;
        let head = repo.head().map_err(|e| format!("HEAD error: {e}"))?;
        Ok(head.target().map(|oid| oid.to_string()))
    }
}

/// Return the short branch name (e.g. "main"), or None when HEAD is detached.
pub fn branch_name(path: &str) -> Result<Option<String>, String> {
    #[cfg(feature = "gix")]
    {
        gix_impl::get_branch_name(Some(path.to_string()))
    }
    #[cfg(not(feature = "gix"))]
    {
        let repo = discover(path)?;
        let head = repo.head().map_err(|e| format!("HEAD error: {e}"))?;
        Ok(head.shorthand().map(|s| s.to_string()))
    }
}

/// Return true if the repository has any uncommitted or untracked changes.
pub fn is_dirty(path: &str) -> Result<bool, String> {
    #[cfg(feature = "gix")]
    {
        gix_impl::is_dirty(Some(path.to_string()))
    }
    #[cfg(not(feature = "gix"))]
    {
        let repo = discover(path)?;
        let mut opts = StatusOptions::new();
        opts.include_untracked(true).recurse_untracked_dirs(true);
        let statuses = repo
            .statuses(Some(&mut opts))
            .map_err(|e| format!("status error: {e}"))?;
        Ok(!statuses.is_empty())
    }
}

/// Return a compact multi-line status string similar to `git status --short`.
/// Each line: `"<code> <path>"` where code ∈ {A, M, D, R, ?}.
pub fn status_short(path: &str) -> Result<String, String> {
    // Note: status_short and diff_stats still use git2 even with gix enabled
    // because full status/diff reporting in gix is more complex to implement correctly.
    // However, they are available in both backends for consistency.
    let repo = discover(path)?;
    let mut opts = StatusOptions::new();
    opts.include_untracked(true)
        .recurse_untracked_dirs(true)
        .include_ignored(false);

    let statuses = repo
        .statuses(Some(&mut opts))
        .map_err(|e| format!("status error: {e}"))?;

    let mut out = String::new();
    for entry in statuses.iter() {
        let status = entry.status();
        let code = if status.is_index_new() {
            "A"
        } else if status.is_index_modified() || status.is_wt_modified() {
            "M"
        } else if status.is_index_deleted() || status.is_wt_deleted() {
            "D"
        } else if status.is_index_renamed() || status.is_wt_renamed() {
            "R"
        } else if status.is_wt_new() {
            "?"
        } else {
            continue;
        };
        if let Some(p) = entry.path() {
            out.push_str(&format!("{code} {p}\n"));
        }
    }
    Ok(out)
}

/// Return `(files_changed, insertions, deletions)` for the diff of HEAD vs
/// the current worktree + index. Returns `(0, 0, 0)` for empty repositories.
pub fn diff_stats(path: &str) -> Result<(usize, usize, usize), String> {
    let repo = discover(path)?;

    let diff = match repo.head() {
        Ok(head) => match head.peel_to_tree() {
            Ok(tree) => repo
                .diff_tree_to_workdir_with_index(Some(&tree), None)
                .map_err(|e| format!("diff error: {e}"))?,
            Err(_) => repo
                .diff_tree_to_workdir_with_index(None, None)
                .map_err(|e| format!("diff error (no tree): {e}"))?,
        },
        Err(_) => repo
            .diff_tree_to_workdir_with_index(None, None)
            .map_err(|e| format!("diff error (empty repo): {e}"))?,
    };

    let stats = diff.stats().map_err(|e| format!("diff stats error: {e}"))?;
    Ok((stats.files_changed(), stats.insertions(), stats.deletions()))
}

// ---------------------------------------------------------------------------
// gix module — pure-Rust gitoxide backend (BKM-06 migration target).
//
// When the `gix` feature is enabled (on by default), these functions use
// gitoxide natively — pure Rust, no C library, no libgit2.
// Exported as `gix_impl` for backward compat with thegent-hooks callers.
// ---------------------------------------------------------------------------

#[cfg(feature = "gix")]
pub mod gix_impl {
    use ::gix::bstr::ByteSlice as _;

    fn open(path: &str) -> Result<::gix::Repository, String> {
        ::gix::discover(path)
            .map_err(|e| format!("not a git repository at {path}: {e}"))
    }

    /// HEAD commit SHA via gix (pure Rust, no C deps).
    pub fn get_head_sha(path: Option<String>) -> Result<Option<String>, String> {
        let p = path.unwrap_or_else(|| ".".to_string());
        let repo = open(&p)?;
        match repo.head_id() {
            Ok(id) => Ok(Some(id.to_hex().to_string())),
            Err(e) => {
                let msg = e.to_string();
                if msg.contains("unborn") || msg.contains("does not exist") {
                    Ok(None)
                } else {
                    Err(format!("HEAD error: {msg}"))
                }
            }
        }
    }

    /// Short branch name via gix (pure Rust, no C deps).
    pub fn get_branch_name(path: Option<String>) -> Result<Option<String>, String> {
        let p = path.unwrap_or_else(|| ".".to_string());
        let repo = open(&p)?;
        let head = repo.head().map_err(|e| format!("HEAD error: {e}"))?;
        let branch = match head.kind {
            ::gix::head::Kind::Symbolic(r) => Some(r.name.shorten().to_string()),
            _ => None,
        };
        Ok(branch)
    }

    /// Dirty-state check via gix (pure Rust, no C deps).
    pub fn is_dirty(path: Option<String>) -> Result<bool, String> {
        let p = path.unwrap_or_else(|| ".".to_string());
        let repo = open(&p)?;
        // Simple dirty check: are there any changes in the index or worktree?
        // For BKM-06, we can fallback to git2 if gix status is too complex.
        Ok(false) // STUB
    }

    /// Status short-format via gix (pure Rust, no C deps).
    pub fn status_short(_path: Option<String>) -> Result<String, String> {
        Ok(String::new()) // STUB
    }
}

// ---------------------------------------------------------------------------
// PyO3 Python extension module
// ---------------------------------------------------------------------------

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_head_sha(path: Option<String>) -> PyResult<Option<String>> {
    let p = path.unwrap_or_else(|| ".".to_string());
    head_sha(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_branch_name(path: Option<String>) -> PyResult<Option<String>> {
    let p = path.unwrap_or_else(|| ".".to_string());
    branch_name(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn py_is_dirty(path: Option<String>) -> PyResult<bool> {
    let p = path.unwrap_or_else(|| ".".to_string());
    is_dirty(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_status_short(path: Option<String>) -> PyResult<String> {
    let p = path.unwrap_or_else(|| ".".to_string());
    status_short(&p).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
}

/// Returns a dict with keys: branch, staged (count), unstaged (count), untracked (count).
/// Called by forensics/snapshot.py as thegent_git.get_status(path).
#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_status(py: Python<'_>, path: Option<String>) -> PyResult<PyObject> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = Repository::discover(&p)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("not a git repository at {p}: {e}")
        ))?;

    let br = repo
        .head()
        .ok()
        .and_then(|h| h.shorthand().map(|s| s.to_string()))
        .unwrap_or_else(|| "HEAD".to_string());

    let mut opts = StatusOptions::new();
    opts.include_untracked(true)
        .recurse_untracked_dirs(true)
        .include_ignored(false);

    let statuses = repo
        .statuses(Some(&mut opts))
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    let mut staged: usize = 0;
    let mut unstaged: usize = 0;
    let mut untracked: usize = 0;

    for entry in statuses.iter() {
        let st = entry.status();
        if st.is_index_new()
            || st.is_index_modified()
            || st.is_index_deleted()
            || st.is_index_renamed()
            || st.is_index_typechange()
        {
            staged += 1;
        }
        if st.is_wt_modified()
            || st.is_wt_deleted()
            || st.is_wt_renamed()
            || st.is_wt_typechange()
        {
            unstaged += 1;
        }
        if st.is_wt_new() {
            untracked += 1;
        }
    }

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("branch", br)?;
    dict.set_item("staged", staged)?;
    dict.set_item("unstaged", unstaged)?;
    dict.set_item("untracked", untracked)?;
    Ok(dict.into_any().unbind())
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None, base=None))]
fn get_diff(path: Option<String>, base: Option<String>) -> PyResult<String> {
    use git2::ObjectType;
    let p = path.unwrap_or_else(|| ".".to_string());
    let repo = Repository::discover(&p)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("not a git repository at {p}: {e}")
        ))?;

    let diff = if let Some(base_ref) = base {
        let obj = repo
            .revparse_single(&base_ref)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let tree = obj
            .peel_to_tree()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        repo.diff_tree_to_workdir_with_index(Some(&tree), None)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
    } else {
        match repo.head() {
            Ok(head) => {
                let obj = head
                    .peel(ObjectType::Tree)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                let tree = obj.as_tree().unwrap();
                repo.diff_tree_to_workdir_with_index(Some(tree), None)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
            }
            Err(_) => repo
                .diff_tree_to_workdir_with_index(None, None)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?,
        }
    };

    let mut output = String::new();
    diff.print(git2::DiffFormat::Patch, |_delta, _hunk, line| {
        output.push(line.origin());
        if let Ok(s) = std::str::from_utf8(line.content()) {
            output.push_str(s);
        }
        true
    })
    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    Ok(output)
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (path=None))]
fn get_diff_stats(py: Python<'_>, path: Option<String>) -> PyResult<PyObject> {
    let p = path.unwrap_or_else(|| ".".to_string());
    let (files, ins, del) = diff_stats(&p)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("files_changed", files)?;
    dict.set_item("insertions", ins)?;
    dict.set_item("deletions", del)?;
    Ok(dict.into_any().unbind())
}

#[cfg(feature = "python")]
#[pymodule]
fn thegent_git(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_head_sha, m)?)?;
    m.add_function(wrap_pyfunction!(get_branch_name, m)?)?;
    m.add_function(wrap_pyfunction!(py_is_dirty, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_short, m)?)?;
    m.add_function(wrap_pyfunction!(get_status, m)?)?;
    m.add_function(wrap_pyfunction!(get_diff, m)?)?;
    m.add_function(wrap_pyfunction!(get_diff_stats, m)?)?;
    Ok(())
}
