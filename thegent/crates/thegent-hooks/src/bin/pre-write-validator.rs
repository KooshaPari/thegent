//! Pre-write-validator hook binary
//!
//! Validates files before they are written: encoding, size, syntax, etc.

#![allow(unused)]

use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct PreWriteValidatorInput {
    /// File path to validate
    file_path: PathBuf,
    /// Maximum file size in bytes
    #[serde(default = "default_max_size")]
    max_size: u64,
    /// Check for UTF-8 encoding
    #[serde(default)]
    check_encoding: bool,
    /// Check for control characters
    #[serde(default)]
    check_control_chars: bool,
    /// Maximum line length
    #[serde(default = "default_max_line_length")]
    max_line_length: usize,
    /// File content (if provided, otherwise read from disk)
    #[serde(default)]
    content: Option<String>,
}

fn default_max_size() -> u64 {
    10 * 1024 * 1024
}
fn default_max_line_length() -> usize {
    1000
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("pre-write-validator: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: PreWriteValidatorInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("pre-write-validator: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    let content = match &input.content {
        Some(c) => c.clone(),
        None => match fs::read_to_string(&input.file_path) {
            Ok(c) => c,
            Err(err) => {
                if err.kind() == std::io::ErrorKind::NotFound {
                    String::new()
                } else {
                    eprintln!("pre-write-validator: failed to read file: {}", err);
                    return ExitCode::from(2);
                }
            }
        },
    };

    // Check file size
    if content.len() as u64 > input.max_size {
        println!(
            r#"{{"valid":false,"errors":[{{"rule":"file_size","message":"File exceeds {} bytes","line":null,"column":null}}],"exit_code":1}}"#,
            input.max_size
        );
        return ExitCode::from(1);
    }

    let mut errors: Vec<String> = Vec::new();

    let check_encoding = input.check_encoding;
    let check_control_chars = input.check_control_chars;

    // Validate encoding
    if check_encoding && !content.is_char_boundary(content.len()) {
        errors.push(
            r#"{"rule":"encoding","message":"Invalid UTF-8","line":null,"column":null}"#
                .to_string(),
        );
    }

    // Validate control characters
    if check_control_chars {
        for (line_num, line) in content.lines().enumerate() {
            for (col_num, c) in line.chars().enumerate() {
                if c.is_control() && c != '\t' && c != '\n' && c != '\r' {
                    let ln = line_num + 1;
                    let col = col_num + 1;
                    errors.push(format!(r#"{{"rule":"control_characters","message":"Control char at {}:{}","line":{},"column":{}}}"#, 
                        ln, col, ln, col));
                }
            }
        }
    }

    // Validate line length
    for (line_num, line) in content.lines().enumerate() {
        if line.len() > input.max_line_length {
            let ln = line_num + 1;
            errors.push(format!(r#"{{"rule":"line_length","message":"Line {} exceeds {} chars","line":{},"column":null}}"#,
                ln, input.max_line_length, ln));
        }
    }

    let valid = errors.is_empty();
    let exit_code = if valid { 0 } else { 1 };

    println!(
        r#"{{"valid":{},"errors":[{}],"exit_code":{}}}"#,
        valid,
        errors.join(","),
        exit_code
    );

    ExitCode::from(exit_code)
}
