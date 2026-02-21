use chrono::{DateTime, FixedOffset};
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

#[pyfunction]
fn parse_checkpoint_by_id(py: Python<'_>, line: &str, checkpoint_id: &str) -> PyResult<Py<PyAny>> {
    let parsed: Value = match serde_json::from_str(line) {
        Ok(v) => v,
        Err(_) => return Ok(py.None().into_bound(py).unbind()),
    };
    let obj = match parsed {
        Value::Object(map) => map,
        _ => return Ok(py.None().into_bound(py).unbind()),
    };
    let matches = obj
        .get("checkpoint_id")
        .and_then(|v| v.as_str())
        .map(|v| v == checkpoint_id)
        .unwrap_or(false);
    if !matches {
        return Ok(py.None().into_bound(py).unbind());
    }
    Ok(serde_to_py(py, Value::Object(obj))?.unbind())
}

#[pyfunction]
#[pyo3(signature = (line, status=None, run_id=None))]
fn parse_dlq_item(
    py: Python<'_>,
    line: &str,
    status: Option<String>,
    run_id: Option<String>,
) -> PyResult<Py<PyAny>> {
    let parsed: Value = match serde_json::from_str(line) {
        Ok(v) => v,
        Err(_) => return Ok(py.None().into_bound(py).unbind()),
    };
    let obj = match parsed {
        Value::Object(map) => map,
        _ => return Ok(py.None().into_bound(py).unbind()),
    };

    if let Some(status_expected) = status {
        let got_status = obj.get("status").and_then(|v| v.as_str()).unwrap_or_default();
        if got_status != status_expected {
            return Ok(py.None().into_bound(py).unbind());
        }
    }

    if let Some(run_id_expected) = run_id {
        let got_run_id = obj.get("run_id").and_then(|v| v.as_str()).unwrap_or_default();
        if got_run_id != run_id_expected {
            return Ok(py.None().into_bound(py).unbind());
        }
    }

    Ok(serde_to_py(py, Value::Object(obj))?.unbind())
}

#[pyfunction]
fn parse_checkpoint_line(py: Python<'_>, line: &str) -> PyResult<Py<PyAny>> {
    let parsed: Value = match serde_json::from_str(line) {
        Ok(v) => v,
        Err(_) => return Ok(py.None().into_bound(py).unbind()),
    };
    match parsed {
        Value::Object(_) => Ok(serde_to_py(py, parsed)?.unbind()),
        _ => Ok(py.None().into_bound(py).unbind()),
    }
}

#[pyfunction]
fn parse_override_unexpired(line: &str, owner: &str, now_iso: &str) -> PyResult<bool> {
    let trimmed = line.trim();
    if trimmed.is_empty() {
        return Ok(false);
    }
    let parsed: Value = match serde_json::from_str(trimmed) {
        Ok(v) => v,
        Err(_) => return Ok(false),
    };
    let obj = match parsed {
        Value::Object(map) => map,
        _ => return Ok(false),
    };
    let got_owner = obj.get("owner").and_then(|v| v.as_str()).unwrap_or_default();
    if got_owner != owner {
        return Ok(false);
    }
    let expires_at = match obj.get("expires_at_utc").and_then(|v| v.as_str()) {
        Some(v) => v,
        None => return Ok(false),
    };
    let now = match DateTime::parse_from_rfc3339(now_iso) {
        Ok(v) => v,
        Err(_) => return Ok(false),
    };
    let expires = match DateTime::parse_from_rfc3339(expires_at) {
        Ok(v) => v,
        Err(_) => return Ok(false),
    };
    Ok(now < expires)
}

#[pyfunction]
fn parse_fatigue_line(line: &str, now_iso: &str, window_s: i64) -> PyResult<u8> {
    let parsed: Value = match serde_json::from_str(line) {
        Ok(v) => v,
        Err(_) => return Ok(0),
    };
    let obj = match parsed {
        Value::Object(map) => map,
        _ => return Ok(0),
    };
    let timestamp = match obj.get("timestamp").and_then(|v| v.as_str()) {
        Some(v) => v,
        None => return Ok(0),
    };
    let now = match DateTime::parse_from_rfc3339(now_iso) {
        Ok(v) => v,
        Err(_) => return Ok(0),
    };
    let ts = match DateTime::parse_from_rfc3339(timestamp) {
        Ok(v) => v,
        Err(_) => return Ok(0),
    };
    let age_s = now.signed_duration_since(ts).num_seconds();
    Ok(if age_s < window_s { 1 } else { 0 })
}

#[pyfunction]
fn parse_circuit_failure(
    line: &str,
    target: &str,
    category: &str,
    now_iso: &str,
    window_s: i64,
) -> PyResult<(u8, Option<String>)> {
    let parsed: Value = match serde_json::from_str(line) {
        Ok(v) => v,
        Err(_) => return Ok((0, None)),
    };
    let obj = match parsed {
        Value::Object(map) => map,
        _ => return Ok((0, None)),
    };

    let got_target = obj.get("target").and_then(|v| v.as_str()).unwrap_or_default();
    let got_category = obj.get("category").and_then(|v| v.as_str()).unwrap_or("agent");
    let got_event = obj.get("event").and_then(|v| v.as_str()).unwrap_or_default();
    if got_target != target || got_category != category || got_event != "failure" {
        return Ok((0, None));
    }

    let timestamp = match obj.get("timestamp").and_then(|v| v.as_str()) {
        Some(v) => v,
        None => return Ok((0, None)),
    };
    let now: DateTime<FixedOffset> = match DateTime::parse_from_rfc3339(now_iso) {
        Ok(v) => v,
        Err(_) => return Ok((0, None)),
    };
    let ts: DateTime<FixedOffset> = match DateTime::parse_from_rfc3339(timestamp) {
        Ok(v) => v,
        Err(_) => return Ok((0, None)),
    };
    let age_s = now.signed_duration_since(ts).num_seconds();
    if age_s < window_s {
        Ok((1, Some(timestamp.to_string())))
    } else {
        Ok((0, None))
    }
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

// ---------------------------------------------------------------------------
// WL-131 B90-W2-B2: Model suffix parser (Rust implementation)
// ---------------------------------------------------------------------------

/// Known routing suffixes for model strings (GW-14 / FR-ROUTE-014).
const KNOWN_SUFFIXES: &[&str] = &[
    "nitro", "floor", "free", "thinking", "online", "extended",
];

/// Result of parsing a model string with optional colon-separated suffix(es).
///
/// Matches the Python `ParsedModel` dataclass signature so that parity tests
/// can compare outputs directly.
#[derive(Debug, Clone, PartialEq)]
pub struct ParsedModelRust {
    /// Model name without suffix(es).
    pub base_model: String,
    /// Ordered list of parsed suffix strings.
    pub suffixes: Vec<String>,
    /// Original input string, preserved unchanged.
    pub raw: String,
}

/// Parse a model string extracting all `:suffix` tokens.
///
/// Supports multiple suffixes: `"model:thinking:online"` yields both
/// `"thinking"` and `"online"`.  Unknown suffix tokens are ignored and do
/// not contribute to `suffixes`.  The first segment before any colon sequence
/// is always the base model.
///
/// # Examples
///
/// ```
/// let r = parse_model_suffixes_rust("gpt-4o:nitro");
/// assert_eq!(r.base_model, "gpt-4o");
/// assert_eq!(r.suffixes, vec!["nitro"]);
/// ```
pub fn parse_model_suffixes_rust(model: &str) -> ParsedModelRust {
    let parts: Vec<&str> = model.split(':').collect();
    let base_model = parts[0].to_string();
    let suffixes: Vec<String> = parts[1..]
        .iter()
        .filter(|p| KNOWN_SUFFIXES.contains(p))
        .map(|p| p.to_string())
        .collect();
    ParsedModelRust {
        base_model,
        suffixes,
        raw: model.to_string(),
    }
}

/// Python-visible wrapper for `parse_model_suffixes_rust`.
///
/// Returns a dict with keys: `base_model`, `suffixes`, `raw`.
#[pyfunction]
fn parse_model_suffixes(py: Python<'_>, model: &str) -> PyResult<Py<PyAny>> {
    let parsed = parse_model_suffixes_rust(model);
    let dict = PyDict::new(py);
    dict.set_item("base_model", parsed.base_model)?;
    let py_suffixes = PyList::new(py, parsed.suffixes.iter())?;
    dict.set_item("suffixes", py_suffixes)?;
    dict.set_item("raw", parsed.raw)?;
    Ok(dict.into_any().unbind())
}

#[cfg(test)]
mod model_suffix_tests {
    use super::*;

    // 10+ parity cases matching tests/routing/test_wl131_parser_parity.py

    #[test]
    fn bare_model_no_suffix() {
        let r = parse_model_suffixes_rust("gpt-4o");
        assert_eq!(r.base_model, "gpt-4o");
        assert!(r.suffixes.is_empty());
        assert_eq!(r.raw, "gpt-4o");
    }

    #[test]
    fn single_suffix_nitro() {
        let r = parse_model_suffixes_rust("gpt-4o:nitro");
        assert_eq!(r.base_model, "gpt-4o");
        assert_eq!(r.suffixes, vec!["nitro"]);
    }

    #[test]
    fn single_suffix_floor() {
        let r = parse_model_suffixes_rust("gpt-4o:floor");
        assert_eq!(r.base_model, "gpt-4o");
        assert_eq!(r.suffixes, vec!["floor"]);
    }

    #[test]
    fn single_suffix_free() {
        let r = parse_model_suffixes_rust("openai/gpt-4o:free");
        assert_eq!(r.base_model, "openai/gpt-4o");
        assert_eq!(r.suffixes, vec!["free"]);
    }

    #[test]
    fn single_suffix_thinking() {
        let r = parse_model_suffixes_rust("claude-sonnet-4-5:thinking");
        assert_eq!(r.base_model, "claude-sonnet-4-5");
        assert_eq!(r.suffixes, vec!["thinking"]);
    }

    #[test]
    fn single_suffix_online() {
        let r = parse_model_suffixes_rust("gpt-4o:online");
        assert_eq!(r.base_model, "gpt-4o");
        assert_eq!(r.suffixes, vec!["online"]);
    }

    #[test]
    fn single_suffix_extended() {
        let r = parse_model_suffixes_rust("claude-opus-4:extended");
        assert_eq!(r.base_model, "claude-opus-4");
        assert_eq!(r.suffixes, vec!["extended"]);
    }

    #[test]
    fn multi_suffix_thinking_online() {
        let r = parse_model_suffixes_rust("anthropic/claude-sonnet-4-5:thinking:online");
        assert_eq!(r.base_model, "anthropic/claude-sonnet-4-5");
        assert_eq!(r.suffixes, vec!["thinking", "online"]);
    }

    #[test]
    fn unknown_suffix_ignored() {
        let r = parse_model_suffixes_rust("model:unknown");
        assert_eq!(r.base_model, "model");
        assert!(r.suffixes.is_empty());
        assert_eq!(r.raw, "model:unknown");
    }

    #[test]
    fn provider_slash_model_no_suffix() {
        let r = parse_model_suffixes_rust("anthropic/claude-opus-4");
        assert_eq!(r.base_model, "anthropic/claude-opus-4");
        assert!(r.suffixes.is_empty());
    }

    #[test]
    fn raw_preserved_with_multi_suffix() {
        let input = "gpt-4o:nitro:thinking";
        let r = parse_model_suffixes_rust(input);
        assert_eq!(r.raw, input);
        assert_eq!(r.suffixes, vec!["nitro", "thinking"]);
    }

    #[test]
    fn empty_string() {
        let r = parse_model_suffixes_rust("");
        assert_eq!(r.base_model, "");
        assert!(r.suffixes.is_empty());
    }
}

#[pymodule]
fn thegent_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_xml_tags, m)?)?;
    m.add_function(wrap_pyfunction!(strip_think_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(strip_noise, m)?)?;
    m.add_function(wrap_pyfunction!(parse_jsonl_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_checkpoint_by_id, m)?)?;
    m.add_function(wrap_pyfunction!(parse_dlq_item, m)?)?;
    m.add_function(wrap_pyfunction!(parse_checkpoint_line, m)?)?;
    m.add_function(wrap_pyfunction!(parse_override_unexpired, m)?)?;
    m.add_function(wrap_pyfunction!(parse_fatigue_line, m)?)?;
    m.add_function(wrap_pyfunction!(parse_circuit_failure, m)?)?;
    m.add_function(wrap_pyfunction!(parse_model_suffixes, m)?)?;
    Ok(())
}
