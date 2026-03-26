//! Integration tests for thegent-subprocess

use thegent_subprocess::domain::entities::{Process, ProcessBuilder};
use thegent_subprocess::domain::value_objects::{ProcessState, ExitStatus};

#[test]
fn test_process_lifecycle() {
    let process = Process::new("echo test".to_string(), vec![]);
    assert_eq!(process.state, ProcessState::Created);
    assert!(process.pid.is_none());
}

#[test]
fn test_process_state_transitions() {
    let mut process = Process::new("sleep 1".to_string(), vec![]);
    assert_eq!(process.state, ProcessState::Created);

    process.start();
    assert_eq!(process.state, ProcessState::Running);

    process.complete(ExitStatus::new(0));
    assert_eq!(process.state, ProcessState::Completed);
}

#[test]
fn test_process_builder() {
    let process = ProcessBuilder::new()
        .command("echo".to_string())
        .arg("hello".to_string())
        .build()
        .unwrap();

    assert_eq!(process.command, "echo");
    assert_eq!(process.args, vec!["hello"]);
}
