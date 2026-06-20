// SPDX-License-Identifier: MIT OR Apache-2.0
//! Integration tests for thegent-shims

#[cfg(test)]
mod tests {
    use std::process::Command;

    #[test]
    fn test_thegent_git_help() {
        let output = Command::new("cargo")
            .args(["run", "--release", "--bin", "thegent-git", "--", "--help"])
            .output();

        assert!(output.is_ok(), "thegent-git --help should work");
    }

    #[test]
    fn test_thegent_grep_help() {
        let output = Command::new("cargo")
            .args(["run", "--release", "--bin", "thegent-grep", "--", "--help"])
            .output();

        assert!(output.is_ok(), "thegent-grep --help should work");
    }

    #[test]
    fn test_thegent_find_help() {
        let output = Command::new("cargo")
            .args(["run", "--release", "--bin", "thegent-find", "--", "--help"])
            .output();

        assert!(output.is_ok(), "thegent-find --help should work");
    }

    #[test]
    fn test_thegent_agent_help() {
        let output = Command::new("cargo")
            .args(["run", "--release", "--bin", "thegent-agent", "--", "--help"])
            .output();

        assert!(output.is_ok(), "thegent-agent --help should work");
    }
}
