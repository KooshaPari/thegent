use thegent_zmx::session::{Session, SessionState};

/// @trace FR-ZMX-010
#[test]
fn test_session_lifecycle() {
    let mut session = Session::new("test-session");
    assert_eq!(session.id(), "test-session");
    assert_eq!(session.state(), SessionState::Created);

    session.transition(SessionState::Active).unwrap();
    assert_eq!(session.state(), SessionState::Active);
}

/// @trace FR-ZMX-011
#[test]
fn test_session_store_retrieve_context() {
    let mut session = Session::new("test");

    let context = std::collections::HashMap::from([
        ("agent_id".to_string(), "agent-1".to_string()),
        ("cost_budget".to_string(), "1.0".to_string()),
    ]);

    session.set_context(context.clone()).unwrap();

    let retrieved = session.get_context().unwrap();
    assert_eq!(retrieved, context);
}

/// @trace FR-ZMX-012
#[test]
fn test_session_state_transitions_valid() {
    let mut session = Session::new("test");

    assert!(session.transition(SessionState::Active).is_ok());
    assert!(session.transition(SessionState::Suspended).is_ok());
    assert!(session.transition(SessionState::Resumed).is_ok());
    assert!(session.transition(SessionState::Closed).is_ok());
}

/// @trace FR-ZMX-012
#[test]
fn test_session_state_transitions_invalid() {
    let mut session = Session::new("test");
    session.transition(SessionState::Active).unwrap();
    session.transition(SessionState::Closed).unwrap();

    assert!(session.transition(SessionState::Active).is_err());
}

/// @trace FR-ZMX-013
#[test]
fn test_session_elapsed_ms() {
    let session = Session::new("test");
    assert!(session.created_at() > 0);

    std::thread::sleep(std::time::Duration::from_millis(50));
    assert!(session.elapsed_ms() >= 50);
}

/// @trace FR-ZMX-012
#[test]
fn test_session_cannot_transition_from_created_to_suspended() {
    let mut session = Session::new("test");
    assert!(session.transition(SessionState::Suspended).is_err());
}

/// @trace FR-ZMX-012
#[test]
fn test_session_can_close_from_created() {
    let mut session = Session::new("test");
    assert!(session.transition(SessionState::Closed).is_ok());
}
