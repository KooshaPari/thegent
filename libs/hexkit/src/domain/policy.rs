//! Domain Policy - Business Rules and Invariants
//!
//! Policies encapsulate complex business rules that govern the behavior of
//! the domain. They are typically stateless rules that evaluate conditions
//! and return decisions.
//!
//! ## When to Use Policies
//!
//! - Complex business rules that span multiple entities
//! - Rules that may change independently from entities
//! - Rules that need to be configurable
//! - Rules that evaluate conditions and return decisions
//!
//! ## Example
//!
//! ```rust
//! use hexkit::domain::policy::*;
//!
//! #[derive(Debug, Clone)]
//! struct DiscountPolicy {
//!     discount_percentage: Decimal,
//!     minimum_order_value: Decimal,
//! }
//!
//! impl Policy for DiscountPolicy {
//!     type Input = Money;
//!     type Output = Money;
//!
//!     fn evaluate(&self, input: &Self::Input) -> Self::Output {
//!         if input.amount >= self.minimum_order_value {
//!             input * self.discount_percentage / 100
//!         } else {
//!             Money::zero()
//!         }
//!     }
//! }
//! ```

/// Marker trait for policies
pub trait Policy: Send + Sync {
    /// Input type for policy evaluation
    type Input;
    /// Output type from policy evaluation
    type Output;

    /// Evaluate the policy with the given input
    fn evaluate(&self, input: &Self::Input) -> Self::Output;

    /// Check if policy applies to the given input
    fn applies_to(&self, input: &Self::Input) -> bool {
        true
    }
}

/// Trait for composable policies
pub trait ComposablePolicy<P>: Policy {
    fn and(self, other: P) -> AndPolicy<Self, P>
    where
        Self: Sized,
        P: Policy<Input = Self::Input>,
    {
        AndPolicy::new(self, other)
    }

    fn or(self, other: P) -> OrPolicy<Self, P>
    where
        Self: Sized,
        P: Policy<Input = Self::Input>,
    {
        OrPolicy::new(self, other)
    }
}

impl<T: Policy, P: Policy<Input = T::Input>> ComposablePolicy<P> for T {}

/// Policy that requires all policies to match
pub struct AndPolicy<A, B> {
    left: A,
    right: B,
}

impl<A, B> AndPolicy<A, B> {
    pub fn new(left: A, right: B) -> Self {
        Self { left, right }
    }
}

impl<A, B> Policy for AndPolicy<A, B>
where
    A: Policy,
    B: Policy<Input = A::Input, Output = A::Output>,
{
    type Input = A::Input;
    type Output = A::Output;

    fn evaluate(&self, input: &Self::Input) -> Self::Output {
        // If left doesn't apply, return default
        if !self.left.applies_to(input) {
            return self.right.evaluate(input);
        }
        // Both apply, combine outputs
        let left_output = self.left.evaluate(input);
        let right_output = self.right.evaluate(input);
        // Combine based on output type - this is generic
        combine_outputs(left_output, right_output)
    }

    fn applies_to(&self, input: &Self::Input) -> bool {
        self.left.applies_to(input) && self.right.applies_to(input)
    }
}

/// Policy that requires any policy to match
pub struct OrPolicy<A, B> {
    left: A,
    right: B,
}

impl<A, B> OrPolicy<A, B> {
    pub fn new(left: A, right: B) -> Self {
        Self { left, right }
    }
}

impl<A, B> Policy for OrPolicy<A, B>
where
    A: Policy,
    B: Policy<Input = A::Input, Output = A::Output>,
{
    type Input = A::Input;
    type Output = A::Output;

    fn evaluate(&self, input: &Self::Input) -> Self::Output {
        if self.left.applies_to(input) {
            self.left.evaluate(input)
        } else {
            self.right.evaluate(input)
        }
    }

    fn applies_to(&self, input: &Self::Input) -> bool {
        self.left.applies_to(input) || self.right.applies_to(input)
    }
}

/// Negation policy
pub struct NotPolicy<P> {
    inner: P,
}

impl<P> NotPolicy<P> {
    pub fn new(inner: P) -> Self {
        Self { inner }
    }
}

impl<P: Policy> Policy for NotPolicy<P>
where
    P: Policy,
{
    type Input = P::Input;
    type Output = bool;

    fn evaluate(&self, input: &Self::Input) -> Self::Output {
        !self.inner.applies_to(input)
    }

    fn applies_to(&self, input: &Self::Input) -> bool {
        true
    }
}

// Helper function - should be specialized per output type
fn combine_outputs<T: Default>(left: T, _right: T) -> T {
    // Default implementation - use first output
    // Override for specific output types
    left
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Clone, PartialEq)]
    struct TestMoney {
        amount: f64,
    }

    impl TestMoney {
        fn new(amount: f64) -> Self {
            Self { amount }
        }
    }

    struct LargeOrderPolicy;
    struct PriorityCustomerPolicy;

    impl Policy for LargeOrderPolicy {
        type Input = TestMoney;
        type Output = bool;

        fn evaluate(&self, input: &Self::Input) -> Self::Output {
            input.amount >= 1000.0
        }

        fn applies_to(&self, input: &Self::Input) -> bool {
            input.amount >= 1000.0
        }
    }

    impl Policy for PriorityCustomerPolicy {
        type Input = TestMoney;
        type Output = bool;

        fn evaluate(&self, _input: &Self::Input) -> Self::Output {
            true
        }

        fn applies_to(&self, _input: &Self::Input) -> bool {
            true
        }
    }

    #[test]
    fn test_or_policy() {
        let policy = OrPolicy::new(LargeOrderPolicy, PriorityCustomerPolicy);

        // Any applies
        assert!(policy.applies_to(&TestMoney::new(100.0)));
        // Only right applies
        assert!(policy.applies_to(&TestMoney::new(100.0)));
    }

    #[test]
    fn test_and_policy() {
        let policy = AndPolicy::new(LargeOrderPolicy, PriorityCustomerPolicy);

        // Both apply
        assert!(policy.applies_to(&TestMoney::new(1000.0)));
        // Only right applies
        assert!(!policy.applies_to(&TestMoney::new(100.0)));
    }
}
