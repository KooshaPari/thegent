//! Test-Driven Development (TDD)
//! 
//! TDD is a development methodology where tests are written before the code.
//! The cycle is: Red -> Green -> Refactor
//! 
//! ## The TDD Cycle
//! 
//! 1. **Red**: Write a failing test
//! 2. **Green**: Write the minimum code to pass
//! 3. **Refactor**: Improve code while keeping tests passing
//! 
//! ## Benefits
//! 
//! - Tests as documentation
//! - Regression protection
//! - Design improvement
//! - Faster debugging
//! 
//! ## Example
//! 
//! ```rust,ignore
//! // RED: Write failing test first
//! #[test]
//! fn order_calculates_discount() {
//!     let order = Order::new();
//!     order.add_item(Item::new("Widget", 100.0), 10);
//!     
//!     // This will fail until we implement the discount logic
//!     assert_eq!(order.total_with_discount(0.1), 900.0);
//! }
//! 
//! // GREEN: Write minimal code to pass
//! impl Order {
//!     pub fn total_with_discount(&self, pct: f64) -> f64 {
//!         self.items.iter().map(|i| i.price * i.qty as f64).sum()
//!             * (1.0 - pct)
//!     }
//! }
//! 
//! // REFACTOR: Clean up while keeping tests green
//! ```

/// Test naming conventions
pub mod naming {
    /// Semantic test name structure: subject_behaves_when_condition
    /// 
    /// Examples:
    /// - order_calculates_total_when_items_exist
    /// - user_fails_validation_when_email_invalid
    /// - payment_processes_successfully_when_card_valid
    pub const SUBJECT_BEHAVES_WHEN: &str = "subject_behaves_when_condition";
}

/// Test categories
pub mod category {
    /// Unit test - tests a single component in isolation
    pub const UNIT: &str = "unit";
    
    /// Integration test - tests interaction between components
    pub const INTEGRATION: &str = "integration";
    
    /// E2E test - tests the entire system
    pub const E2E: &str = "e2e";
}

/// TDD-specific test attributes
pub mod attributes {
    /// Marks a test as a TDD-style red-green-refactor test
    pub const TDD_TEST: &str = "#[test]";
    
    /// Marks a test as a property-based test
    pub const PROPERTY_TEST: &str = "#[proptest]";
}

/// Test result types
pub mod result {
    /// TDD test result with context
    #[derive(Debug)]
    pub struct TddResult<T> {
        pub value: T,
        pub iterations: u32,
        pub execution_time_ms: u64,
    }
    
    impl<T> TddResult<T> {
        pub fn new(value: T) -> Self {
            Self {
                value,
                iterations: 1,
                execution_time_ms: 0,
            }
        }
    }
}

/// Given-When-Then helper structure
pub mod given_when_then {
    /// Test builder for Given-When-Then pattern
    pub struct TestBuilder<T> {
        given: Option<Box<dyn FnOnce() -> T>>,
        when: Option<Box<dyn FnOnce(&T)>>,
        then: Option<Box<dyn FnOnce(&T)>>,
    }
    
    impl<T> TestBuilder<T> {
        pub fn new() -> Self {
            Self {
                given: None,
                when: None,
                then: None,
            }
        }
        
        /// Set up the test context (Given)
        pub fn given<F>(mut self, setup: F) -> Self 
        where F: FnOnce() -> T + 'static
        {
            self.given = Some(Box::new(setup));
            self
        }
        
        /// Execute the action (When)
        pub fn when<F>(mut self, action: F) -> Self 
        where F: FnOnce(&T) + 'static
        {
            self.when = Some(Box::new(action));
            self
        }
        
        /// Assert the expected outcome (Then)
        pub fn then<F>(mut self, assertion: F) -> Self 
        where F: FnOnce(&T) + 'static
        {
            self.then = Some(Box::new(assertion));
            self
        }
        
        /// Execute the test
        pub fn run(self) {
            if let Some(given) = self.given {
                let context = given();
                if let Some(when) = self.when {
                    when(&context);
                    if let Some(then) = self.then {
                        then(&context);
                    }
                }
            }
        }
    }
    
    impl<T> Default for TestBuilder<T> {
        fn default() -> Self {
            Self::new()
        }
    }
}
