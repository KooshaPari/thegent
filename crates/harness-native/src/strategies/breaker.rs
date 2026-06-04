// Placeholder for breaker module.
use std::path::Path;

#[allow(dead_code)]
pub fn is_tripped(_path: &Path) -> bool {
    // TODO: replace with persisted breaker-state lookup.
    false
}
