use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// Session lifecycle states with enforced state machine transitions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SessionState {
    Created,
    Active,
    Suspended,
    Resumed,
    Closed,
}

impl SessionState {
    pub fn as_str(&self) -> &'static str {
        match self {
            SessionState::Created => "Created",
            SessionState::Active => "Active",
            SessionState::Suspended => "Suspended",
            SessionState::Resumed => "Resumed",
            SessionState::Closed => "Closed",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "Created" => Some(SessionState::Created),
            "Active" => Some(SessionState::Active),
            "Suspended" => Some(SessionState::Suspended),
            "Resumed" => Some(SessionState::Resumed),
            "Closed" => Some(SessionState::Closed),
            _ => None,
        }
    }
}

impl std::fmt::Display for SessionState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// A managed session with state machine transitions and context storage.
pub struct Session {
    id: String,
    state: SessionState,
    context: HashMap<String, String>,
    created_at: u64,
}

impl Session {
    pub fn new(id: &str) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock before epoch")
            .as_millis() as u64;

        Self {
            id: id.to_string(),
            state: SessionState::Created,
            context: HashMap::new(),
            created_at: now,
        }
    }

    pub fn id(&self) -> &str {
        &self.id
    }

    pub fn state(&self) -> SessionState {
        self.state
    }

    pub fn transition(&mut self, new_state: SessionState) -> Result<(), String> {
        let valid = match self.state {
            SessionState::Created => {
                matches!(new_state, SessionState::Active | SessionState::Closed)
            }
            SessionState::Active => {
                matches!(new_state, SessionState::Suspended | SessionState::Closed)
            }
            SessionState::Suspended => {
                matches!(new_state, SessionState::Resumed | SessionState::Closed)
            }
            SessionState::Resumed => {
                matches!(new_state, SessionState::Suspended | SessionState::Closed)
            }
            SessionState::Closed => false,
        };

        if !valid {
            return Err(format!(
                "Invalid transition from {} to {}",
                self.state.as_str(),
                new_state.as_str()
            ));
        }

        self.state = new_state;
        Ok(())
    }

    pub fn set_context(&mut self, context: HashMap<String, String>) -> Result<(), String> {
        self.context = context;
        Ok(())
    }

    pub fn get_context(&self) -> Result<HashMap<String, String>, String> {
        Ok(self.context.clone())
    }

    pub fn created_at(&self) -> u64 {
        self.created_at
    }

    pub fn elapsed_ms(&self) -> u64 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock before epoch")
            .as_millis() as u64;
        now - self.created_at
    }
}
