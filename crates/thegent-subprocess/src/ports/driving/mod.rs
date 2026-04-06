//! # Driving Ports (Primary Ports)
//!
//! Interfaces that the application uses to interact with external actors.

/// CLI interface for subprocess management
pub trait CliPort {
    /// Display process status
    fn display_process(&self, process_id: &str);

    /// Display process list
    fn display_processes(&self, processes: Vec<String>);

    /// Display error
    fn display_error(&self, error: &str);

    /// Display success
    fn display_success(&self, message: &str);
}

/// HTTP/REST interface
pub trait HttpPort {
    /// Handle spawn request
    fn handle_spawn(&self, cmd: Vec<String>, cwd: Option<String>, env: Option<Vec<(String, String)>>) -> Result<String, String>;

    /// Handle kill request
    fn handle_kill(&self, process_id: &str) -> Result<(), String>;

    /// Handle status request
    fn handle_status(&self, process_id: &str) -> Result<String, String>;

    /// Handle list request
    fn handle_list(&self) -> Result<Vec<String>, String>;
}
