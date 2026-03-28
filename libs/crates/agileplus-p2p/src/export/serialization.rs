use std::collections::BTreeMap;

use serde_json::Value;

/// Recursively convert a `serde_json::Value` so that all Object variants use
/// `BTreeMap` (which serializes with sorted keys).
pub fn to_sorted(v: Value) -> Value {
    match v {
        Value::Object(map) => {
            let sorted: BTreeMap<String, Value> =
                map.into_iter().map(|(k, v)| (k, to_sorted(v))).collect();
            Value::Object(sorted.into_iter().collect())
        }
        Value::Array(arr) => Value::Array(arr.into_iter().map(to_sorted).collect()),
        other => other,
    }
}

pub fn to_sorted_pretty(v: Value) -> Result<String, serde_json::Error> {
    let sorted = to_sorted(v);
    serde_json::to_string_pretty(&sorted)
}

pub fn to_sorted_line(v: Value) -> Result<String, serde_json::Error> {
    let sorted = to_sorted(v);
    serde_json::to_string(&sorted)
}
