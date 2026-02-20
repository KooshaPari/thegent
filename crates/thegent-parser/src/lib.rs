use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::sync::OnceLock;

/// Tag name pattern: alphanumeric, underscore, hyphen.
static TAG_RE: OnceLock<Regex> = OnceLock::new();

fn tag_re() -> &'static Regex {
    TAG_RE.get_or_init(|| Regex::new(r"<([A-Za-z0-9_\-]+)>").unwrap())
}

/// BKM-02: Extract XML tags of form <TAG>value</TAG> into a dict.
/// Uses manual matching (Rust regex crate does not support backreferences).
#[pyfunction]
#[pyo3(signature = (text, allowed_tags=None, case_sensitive=false))]
fn extract_xml_tags(
    text: &str,
    allowed_tags: Option<Vec<String>>,
    case_sensitive: bool,
) -> PyResult<HashMap<String, String>> {
    let mut tags: HashMap<String, String> = HashMap::new();
    let mut search_start = 0;
    while let Some(cap) = tag_re().captures(&text[search_start..]) {
        let key = cap.get(1).map(|m| m.as_str().to_string()).unwrap_or_default();
        let open_full = cap.get(0).unwrap();
        let content_start = search_start + open_full.end();
        let closing = format!("</{}>", key);
        if let Some(close_pos) = text[content_start..].find(&closing) {
            let val = text[content_start..content_start + close_pos].trim().to_string();
            let include = match &allowed_tags {
                None => true,
                Some(t) => {
                    if case_sensitive {
                        t.contains(&key)
                    } else {
                        t.iter().any(|tag| tag.eq_ignore_ascii_case(&key))
                    }
                }
            };
            if include {
                tags.insert(key, val);
            }
            search_start = content_start + close_pos + closing.len();
        } else {
            search_start = content_start;
        }
    }
    Ok(tags)
}

/// BKM-02: Remove <think>...</think> blocks from text.
#[pyfunction]
fn strip_think_blocks(text: &str) -> String {
    let re = Regex::new(r"(?s)<think>.*?</think>").unwrap();
    re.replace_all(text, "").trim().to_string()
}

/// BKM-02: Strip noise lines by profile. Profiles: "plain", "jsonl", "leading".
#[pyfunction]
#[pyo3(signature = (text, profile="plain"))]
fn strip_noise(text: &str, profile: &str) -> String {
    let re_time = Regex::new(r"^\[TIME CONSTRAINT").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_tool_calls = Regex::new(r"^You have approximately \d+ tool calls").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_ok = Regex::new(r"^\s*OK\s*$").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_turn = Regex::new(r#"^\s*\{\s*"type"\s*:\s*"turn\.(completed|started)"#).unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_thread = Regex::new(r#"^\s*\{\s*"type"\s*:\s*"thread\.started"#).unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_total = Regex::new(r"^Total usage est:").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_duration = Regex::new(r"^Total duration \(API\):").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_usage = Regex::new(r"^Usage by model:").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_ok_prefix = Regex::new(r"^\[OK\] ").unwrap_or_else(|_| Regex::new("$^").unwrap());
    let re_exit = Regex::new(r"^exit=\d+").unwrap_or_else(|_| Regex::new("$^").unwrap());

    let lines: Vec<&str> = text.lines().collect();
    let mut out: Vec<&str> = Vec::new();
    let mut stripped_leading = 0usize;

    for line in lines {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            out.push(line);
            continue;
        }

        if profile == "leading" || profile == "plain" {
            let is_leading = re_time.is_match(trimmed) || re_tool_calls.is_match(trimmed) || re_ok.is_match(trimmed);
            if is_leading && stripped_leading < 5 {
                stripped_leading += 1;
                continue;
            }
        }

        if profile == "jsonl" || profile == "plain" {
            if re_turn.is_match(trimmed) || re_thread.is_match(trimmed) {
                continue;
            }
        }

        if profile == "plain" {
            if re_total.is_match(trimmed)
                || re_duration.is_match(trimmed)
                || re_usage.is_match(trimmed)
                || re_ok_prefix.is_match(trimmed)
                || re_exit.is_match(trimmed)
            {
                continue;
            }
        }

        out.push(line);
    }
    out.join("\n")
}

#[pyfunction]
fn parse_jsonl_file(py: Python<'_>, path: String) -> PyResult<Py<PyAny>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let list = PyList::empty(py);

    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let v: Value = serde_json::from_str(&line).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON parse error: {}", e))
        })?;

        let obj = serde_to_py(py, v)?;
        list.append(obj)?;
    }

    Ok(list.into_any().unbind())
}

fn serde_to_py<'py>(py: Python<'py>, v: Value) -> PyResult<Bound<'py, PyAny>> {
    match v {
        Value::Null => Ok(py.None().into_bound(py)),
        Value::Bool(b) => {
            let obj = b.into_pyobject(py)?;
            Ok((*obj).clone().into_any())
        }
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                let obj = i.into_pyobject(py)?;
                Ok((*obj).clone().into_any())
            } else if let Some(f) = n.as_f64() {
                let obj = f.into_pyobject(py)?;
                Ok((*obj).clone().into_any())
            } else {
                let obj = n.to_string().into_pyobject(py)?;
                Ok((*obj).clone().into_any())
            }
        }
        Value::String(s) => {
            let obj = s.into_pyobject(py)?;
            Ok((*obj).clone().into_any())
        }
        Value::Array(arr) => {
            let list = PyList::empty(py);
            for item in arr {
                list.append(serde_to_py(py, item)?)?;
            }
            Ok(list.into_any())
        }
        Value::Object(obj) => {
            let dict = PyDict::new(py);
            for (k, v) in obj {
                dict.set_item(k, serde_to_py(py, v)?)?;
            }
            Ok(dict.into_any())
        }
    }
}

#[pymodule]
fn thegent_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_xml_tags, m)?)?;
    m.add_function(wrap_pyfunction!(strip_think_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(strip_noise, m)?)?;
    m.add_function(wrap_pyfunction!(parse_jsonl_file, m)?)?;
    Ok(())
}
