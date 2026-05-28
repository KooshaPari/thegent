use regex::Regex;
use serde::Serialize;
use std::sync::OnceLock;

/// A named secret pattern entry: (type_name, compiled regex).
pub struct SecretPattern {
    pub kind: &'static str,
    pub regex: Regex,
}

/// A single secret match found during scanning.
#[derive(Serialize)]
pub struct SecretMatch {
    /// Human-readable type label (e.g. "openai_api_key").
    pub kind: String,
    /// 1-based line number of the match.
    pub line: usize,
    /// Masked version of the matched text (never the raw secret).
    pub masked: String,
}

/// Top-level JSON output for `hook-dispatcher scan-secrets`.
#[derive(Serialize)]
pub struct ScanSecretsOutput {
    pub found: bool,
    pub matches: Vec<SecretMatch>,
}

/// Return the lazily-initialized list of named secret patterns.
pub fn get_named_secret_patterns() -> &'static Vec<SecretPattern> {
    static PATTERNS: OnceLock<Vec<SecretPattern>> = OnceLock::new();
    PATTERNS.get_or_init(|| {
        vec![
            SecretPattern {
                kind: "openai_api_key",
                regex: Regex::new(r"sk-[a-zA-Z0-9]{48}").unwrap(),
            },
            SecretPattern {
                kind: "openai_proj_key",
                regex: Regex::new(r"sk-proj-[a-zA-Z0-9_-]{48,}").unwrap(),
            },
            SecretPattern {
                kind: "anthropic_api_key",
                regex: Regex::new(r"sk-ant-[a-zA-Z0-9_-]{90,}").unwrap(),
            },
            SecretPattern {
                kind: "google_cloud_key",
                regex: Regex::new(r"AIza[0-9A-Za-z\-_]{35}").unwrap(),
            },
            SecretPattern {
                kind: "slack_token",
                regex: Regex::new(r"xox[baprs]-[0-9A-Za-z\-]{10,}").unwrap(),
            },
            SecretPattern {
                kind: "private_key_block",
                regex: Regex::new(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----").unwrap(),
            },
            SecretPattern {
                kind: "square_access_token",
                regex: Regex::new(r"sq0atp-[0-9A-Za-z\-_]{22}").unwrap(),
            },
            SecretPattern {
                kind: "aws_access_key_id",
                regex: Regex::new(r"AKIA[0-9A-Z]{16}").unwrap(),
            },
            SecretPattern {
                kind: "aws_secret_key_context",
                regex: Regex::new(
                    r"(?i)(aws_secret_access_key|secret_access_key)\s*[=:]\s*\S{20,}",
                )
                .unwrap(),
            },
            SecretPattern {
                kind: "github_pat",
                regex: Regex::new(r"ghp_[a-zA-Z0-9]{36}").unwrap(),
            },
            SecretPattern {
                kind: "github_oauth",
                regex: Regex::new(r"gho_[a-zA-Z0-9]{36}").unwrap(),
            },
            SecretPattern {
                kind: "github_app_token",
                regex: Regex::new(r"ghs_[a-zA-Z0-9]{36}").unwrap(),
            },
            SecretPattern {
                kind: "generic_hex_secret",
                regex: Regex::new(
                    r"(?i)(password|secret|token|api[_-]?key)\s*[=:]\s*[0-9a-f]{20,}",
                )
                .unwrap(),
            },
            SecretPattern {
                kind: "generic_base64_secret",
                regex: Regex::new(
                    r"(?i)(password|secret|token|api[_-]?key)\s*[=:]\s*[A-Za-z0-9+/]{32,}={0,2}",
                )
                .unwrap(),
            },
        ]
    })
}

/// Mask a matched string: keep first 4 chars + `****` + last 2 chars if long enough.
pub fn mask_secret(matched: &str) -> String {
    let chars: Vec<char> = matched.chars().collect();
    if chars.len() <= 8 {
        return "****".to_string();
    }
    let prefix: String = chars[..4].iter().collect();
    let suffix: String = chars[chars.len() - 2..].iter().collect();
    format!("{prefix}****{suffix}")
}

/// Scan `content` line-by-line for secrets. Returns all matches with masking.
pub fn scan_content_for_secrets(content: &str) -> Vec<SecretMatch> {
    let patterns = get_named_secret_patterns();
    let mut matches: Vec<SecretMatch> = Vec::new();

    for (line_idx, line) in content.lines().enumerate() {
        let line_no = line_idx + 1;
        for pat in patterns {
            if let Some(m) = pat.regex.find(line) {
                matches.push(SecretMatch {
                    kind: pat.kind.to_string(),
                    line: line_no,
                    masked: mask_secret(m.as_str()),
                });
                // One match per pattern per line is enough
                break;
            }
        }
    }

    matches
}

/// Backward-compat helper used by run_governance_scan: returns count of files with secrets.
pub fn get_secret_regexes() -> &'static Vec<Regex> {
    static SECRET_REGEXES: OnceLock<Vec<Regex>> = OnceLock::new();
    SECRET_REGEXES.get_or_init(|| {
        get_named_secret_patterns()
            .iter()
            .map(|p| Regex::new(p.regex.as_str()).unwrap())
            .collect()
    })
}
