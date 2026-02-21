use std::fs;
use std::io::{self, Read};
use std::path::Path;

use base16ct::lower;
use blake3::Hasher;
use serde_json::Value;

use crate::Error;

pub(crate) fn read_input() -> Result<Value, Error> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    if input.trim().is_empty() {
        Ok(Value::Null)
    } else {
        Ok(serde_json::from_str(&input)?)
    }
}

pub(crate) fn compute_blake3_hash(content: &str) -> String {
    let mut hasher = Hasher::new();
    hasher.update(content.as_bytes());
    let hash = hasher.finalize();
    let bytes = hash.as_bytes();
    let mut buf = vec![0u8; bytes.len() * 2];
    let encoded = lower::encode(bytes, &mut buf).unwrap();
    String::from_utf8_lossy(encoded).to_string()
}

pub(crate) fn compute_file_hash(path: &Path) -> io::Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hasher = Hasher::new();
    let mut buffer = [0; 8192];
    loop {
        let count = file.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        hasher.update(&buffer[..count]);
    }
    let hash = hasher.finalize();
    let bytes = hash.as_bytes();
    let mut buf = vec![0u8; bytes.len() * 2];
    let encoded = lower::encode(bytes, &mut buf).unwrap();
    Ok(String::from_utf8_lossy(encoded).to_string())
}
