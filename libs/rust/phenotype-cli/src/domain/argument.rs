//! Argument types for CLI commands.

use core::fmt;

/// Argument value types.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ArgValue {
    String(String),
    Integer(i64),
    Float(f64),
    Boolean(bool),
}

impl ArgValue {
    /// Get as string.
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Self::String(s) => Some(s),
            _ => None,
        }
    }

    /// Get as integer.
    pub fn as_integer(&self) -> Option<i64> {
        match self {
            Self::Integer(i) => Some(*i),
            Self::String(s) => s.parse().ok(),
            _ => None,
        }
    }

    /// Get as float.
    pub fn as_float(&self) -> Option<f64> {
        match self {
            Self::Float(f) => Some(*f),
            Self::Integer(i) => Some(*i as f64),
            Self::String(s) => s.parse().ok(),
            _ => None,
        }
    }

    /// Get as boolean.
    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Self::Boolean(b) => Some(*b),
            Self::String(s) => match s.to_lowercase().as_str() {
                "true" | "1" | "yes" | "on" => Some(true),
                "false" | "0" | "no" | "off" => Some(false),
                _ => None,
            },
            _ => None,
        }
    }
}

impl fmt::Display for ArgValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::String(s) => write!(f, "{}", s),
            Self::Integer(i) => write!(f, "{}", i),
            Self::Float(fl) => write!(f, "{}", fl),
            Self::Boolean(b) => write!(f, "{}", b),
        }
    }
}

/// Argument type.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ArgType {
    /// Positional argument.
    Positional,
    /// Short option (-o).
    Short,
    /// Long option (--option).
    Long,
    /// Flag (boolean option).
    Flag,
}

impl ArgType {
    /// Get the prefix for this argument type.
    pub fn prefix(&self) -> &'static str {
        match self {
            Self::Positional => "",
            Self::Short => "-",
            Self::Long => "--",
            Self::Flag => "-",
        }
    }
}

/// Argument for CLI commands.
#[derive(Debug, Clone)]
pub struct Argument {
    name: String,
    arg_type: ArgType,
    short: Option<char>,
    long: Option<String>,
    about: Option<String>,
    required: bool,
    multiple: bool,
    default_value: Option<ArgValue>,
    possible_values: Vec<String>,
    env_var: Option<String>,
}

impl Argument {
    /// Create a new positional argument.
    pub fn positional(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            arg_type: ArgType::Positional,
            short: None,
            long: None,
            about: None,
            required: false,
            multiple: false,
            default_value: None,
            possible_values: Vec::new(),
            env_var: None,
        }
    }

    /// Create a new long option argument.
    pub fn long(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            arg_type: ArgType::Long,
            short: None,
            long: Some(name.into()),
            about: None,
            required: false,
            multiple: false,
            default_value: None,
            possible_values: Vec::new(),
            env_var: None,
        }
    }

    /// Create a new short option argument.
    pub fn short(c: char) -> Self {
        Self {
            name: c.to_string(),
            arg_type: ArgType::Short,
            short: Some(c),
            long: None,
            about: None,
            required: false,
            multiple: false,
            default_value: None,
            possible_values: Vec::new(),
            env_var: None,
        }
    }

    /// Create a new flag argument.
    pub fn flag(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            arg_type: ArgType::Flag,
            short: None,
            long: Some(name.into()),
            about: None,
            required: false,
            multiple: false,
            default_value: None,
            possible_values: Vec::new(),
            env_var: None,
        }
    }

    /// Set the short name.
    pub fn short(mut self, c: char) -> Self {
        self.short = Some(c);
        self
    }

    /// Set the long name.
    pub fn long(mut self, name: impl Into<String>) -> Self {
        self.long = Some(name.into());
        self
    }

    /// Set the description.
    pub fn about(mut self, about: impl Into<String>) -> Self {
        self.about = Some(about.into());
        self
    }

    /// Mark as required.
    pub fn required(mut self) -> Self {
        self.required = true;
        self
    }

    /// Allow multiple values.
    pub fn multiple(mut self) -> Self {
        self.multiple = true;
        self
    }

    /// Set a default value.
    pub fn default(mut self, value: ArgValue) -> Self {
        self.default_value = Some(value);
        self
    }

    /// Set possible values.
    pub fn possible_values(mut self, values: impl IntoIterator<Item = impl Into<String>>) -> Self {
        self.possible_values = values.into_iter().map(|v| v.into()).collect();
        self
    }

    /// Set environment variable.
    pub fn env_var(mut self, name: impl Into<String>) -> Self {
        self.env_var = Some(name.into());
        self
    }

    /// Get name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get type.
    pub fn arg_type(&self) -> ArgType {
        self.arg_type
    }

    /// Get short name.
    pub fn short(&self) -> Option<char> {
        self.short
    }

    /// Get long name.
    pub fn long(&self) -> Option<&str> {
        self.long.as_deref()
    }

    /// Get description.
    pub fn about(&self) -> Option<&str> {
        self.about.as_deref()
    }

    /// Check if required.
    pub fn is_required(&self) -> bool {
        self.required
    }

    /// Check if multiple.
    pub fn is_multiple(&self) -> bool {
        self.multiple
    }

    /// Get default value.
    pub fn default_value(&self) -> Option<&ArgValue> {
        self.default_value.as_ref()
    }

    /// Get possible values.
    pub fn possible_values(&self) -> &[String] {
        &self.possible_values
    }

    /// Get environment variable.
    pub fn env_var(&self) -> Option<&str> {
        self.env_var.as_deref()
    }
}

impl fmt::Display for Argument {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.arg_type {
            ArgType::Positional => write!(f, "{}", self.name),
            ArgType::Short => write!(f, "-{}", self.short.unwrap_or_default()),
            ArgType::Long => write!(f, "--{}", self.long.as_ref().unwrap_or(&self.name)),
            ArgType::Flag => write!(f, "--{}", self.long.as_ref().unwrap_or(&self.name)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_positional_argument() {
        let arg = Argument::positional("name")
            .required()
            .about("The name to greet");
        
        assert_eq!(arg.name(), "name");
        assert!(arg.is_required());
        assert_eq!(arg.arg_type(), ArgType::Positional);
    }

    #[test]
    fn test_option_argument() {
        let arg = Argument::long("output")
            .short('o')
            .about("Output file");
        
        assert_eq!(arg.name(), "output");
        assert_eq!(arg.short(), Some('o'));
        assert_eq!(arg.long(), Some("output"));
    }

    #[test]
    fn test_arg_value_conversion() {
        assert_eq!(ArgValue::String("42".to_string()).as_integer(), Some(42));
        assert_eq!(ArgValue::Integer(42).as_str(), None);
        assert_eq!(ArgValue::Boolean(true).as_bool(), Some(true));
    }
}
