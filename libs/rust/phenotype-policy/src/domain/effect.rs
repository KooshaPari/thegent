//! Effect - The result of a policy evaluation.
//!
//! Following the ALLOW/DENY model from XACML and AWS IAM:
//! - Allow - permits the action
//! - Deny - forbids the action
//! - NotApplicable - policy doesn't apply
//! - Indeterminate - evaluation error

use std::fmt;

/// The effect of a policy rule or policy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Effect {
    /// Allow the action (permit)
    Allow,
    /// Deny the action (forbid)
    Deny,
    /// The policy doesn't apply to this request
    NotApplicable,
    /// Evaluation resulted in an error
    Indeterminate,
}

impl Effect {
    /// Check if this effect allows the action.
    pub fn is_allow(&self) -> bool {
        matches!(self, Effect::Allow)
    }

    /// Check if this effect denies the action.
    pub fn is_deny(&self) -> bool {
        matches!(self, Effect::Deny)
    }

    /// Check if this effect is not applicable.
    pub fn is_not_applicable(&self) -> bool {
        matches!(self, Effect::NotApplicable)
    }

    /// Check if this effect indicates an error.
    pub fn is_indeterminate(&self) -> bool {
        matches!(self, Effect::Indeterminate)
    }

    /// Combine two effects according to XACML combining algorithms.
    ///
    /// For deny-overrides: if either is Deny, result is Deny
    /// For permit-overrides: if either is Allow, result is Allow
    pub fn combine_deny_overrides(self, other: Effect) -> Effect {
        match (self, other) {
            (Effect::Deny, _) | (_, Effect::Deny) => Effect::Deny,
            (Effect::Indeterminate, _) | (_, Effect::Indeterminate) => Effect::Indeterminate,
            (Effect::Allow, _) | (_, Effect::Allow) => Effect::Allow,
            _ => Effect::NotApplicable,
        }
    }

    pub fn combine_permit_overrides(self, other: Effect) -> Effect {
        match (self, other) {
            (Effect::Allow, _) | (_, Effect::Allow) => Effect::Allow,
            (Effect::Indeterminate, _) | (_, Effect::Indeterminate) => Effect::Indeterminate,
            (Effect::Deny, _) | (_, Effect::Deny) => Effect::Deny,
            _ => Effect::NotApplicable,
        }
    }

    /// First applicable effect (stop on first non-NotApplicable)
    pub fn combine_first_applicable(self, other: Effect) -> Effect {
        match self {
            Effect::NotApplicable => other,
            _ => self,
        }
    }
}

impl Default for Effect {
    fn default() -> Self {
        Effect::NotApplicable
    }
}

impl fmt::Display for Effect {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Effect::Allow => write!(f, "ALLOW"),
            Effect::Deny => write!(f, "DENY"),
            Effect::NotApplicable => write!(f, "NOT_APPLICABLE"),
            Effect::Indeterminate => write!(f, "INDETERMINATE"),
        }
    }
}

impl std::str::FromStr for Effect {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "ALLOW" | "PERMIT" | "TRUE" => Ok(Effect::Allow),
            "DENY" | "FORBID" | "FALSE" => Ok(Effect::Deny),
            "NOT_APPLICABLE" | "NA" | "N/A" => Ok(Effect::NotApplicable),
            "INDETERMINATE" | "ERROR" => Ok(Effect::Indeterminate),
            _ => Err(format!("Unknown effect: {}", s)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_deny_overrides() {
        assert_eq!(Effect::Allow.combine_deny_overrides(Effect::Allow), Effect::Allow);
        assert_eq!(Effect::Allow.combine_deny_overrides(Effect::Deny), Effect::Deny);
        assert_eq!(Effect::Deny.combine_deny_overrides(Effect::Allow), Effect::Deny);
        assert_eq!(Effect::NotApplicable.combine_deny_overrides(Effect::Allow), Effect::Allow);
    }

    #[test]
    fn test_permit_overrides() {
        assert_eq!(Effect::Allow.combine_permit_overrides(Effect::Allow), Effect::Allow);
        assert_eq!(Effect::Allow.combine_permit_overrides(Effect::Deny), Effect::Allow);
        assert_eq!(Effect::Deny.combine_permit_overrides(Effect::Allow), Effect::Allow);
        assert_eq!(Effect::NotApplicable.combine_permit_overrides(Effect::Allow), Effect::Allow);
    }

    #[test]
    fn test_parse() {
        assert_eq!("ALLOW".parse::<Effect>().unwrap(), Effect::Allow);
        assert_eq!("deny".parse::<Effect>().unwrap(), Effect::Deny);
        assert!("invalid".parse::<Effect>().is_err());
    }
}
