//! Email value object
//! 
//! Validates and wraps email addresses.

use std::fmt;
use std::error::Error;
use regex::Regex;

#[derive(Clone, PartialEq, Eq)]
pub struct Email(String);

#[derive(Debug)]
pub enum EmailError {
    InvalidFormat,
}

impl fmt::Display for EmailError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EmailError::InvalidFormat => write!(f, "Invalid email format"),
        }
    }
}

impl Error for EmailError {}

impl Email {
    /// Create a new Email, validating the format
    pub fn new(address: &str) -> Result<Self, EmailError> {
        let email_regex = Regex::new(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        ).expect("Invalid email regex");
        
        if email_regex.is_match(address) {
            Ok(Self(address.to_lowercase()))
        } else {
            Err(EmailError::InvalidFormat)
        }
    }
    
    /// Get the email address as a string
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Debug for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Email({})", self.0)
    }
}

impl fmt::Display for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}
