//! Common value object primitives
//! 
//! Provides common value objects that can be used across domains.

pub mod email;
pub mod money;
pub mod timestamp;

pub use email::Email;
pub use money::Money;
pub use timestamp::Timestamp;
