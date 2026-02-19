use pyo3::prelude::*;
use pyo3::types::PyList;
use std::fs::File;
use std::io::{BufRead, BufReader};
use serde_json::Value;

#[pyfunction]
fn parse_jsonl_file(py: Python<'_>, path: String) -> PyResult<PyObject> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let list = PyList::empty_bound(py);

    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let v: Value = serde_json::from_str(&line).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON parse error: {}", e))
        })?;
        
        // Convert serde_json::Value to PyObject
        let obj = serde_to_py(py, v)?;
        list.append(obj)?;
    }

    Ok(list.into())
}

fn serde_to_py(py: Python<'_>, v: Value) -> PyResult<PyObject> {
    match v {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(b.to_object(py)),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.to_object(py))
            } else if let Some(f) = n.as_f64() {
                Ok(f.to_object(py))
            } else {
                Ok(n.to_string().to_object(py))
            }
        }
        Value::String(s) => Ok(s.to_object(py)),
        Value::Array(arr) => {
            let list = PyList::empty_bound(py);
            for item in arr {
                list.append(serde_to_py(py, item)?)?;
            }
            Ok(list.into())
        }
        Value::Object(obj) => {
            let dict = pyo3::types::PyDict::new_bound(py);
            for (k, v) in obj {
                dict.set_item(k, serde_to_py(py, v)?)?;
            }
            Ok(dict.into())
        }
    }
}

#[pymodule]
fn thegent_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_jsonl_file, m)?)?;
    Ok(())
}
