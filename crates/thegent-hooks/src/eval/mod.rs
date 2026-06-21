// SPDX-License-Identifier: MIT OR Apache-2.0
use serde_json::Value;

pub(crate) fn json_dotted_number(root: &Value, dotted: &str) -> Option<f64> {
    let mut cur = root;
    for part in dotted.split('.') {
        cur = cur.get(part)?;
    }
    cur.as_f64()
}
