//! Specification-Driven Development (SDD)
//! 
//! SDD emphasizes creating detailed specifications before implementation.
//! Unlike BDD's behavior focus, SDD focuses on technical specifications.
//! 
//! ## SDD in Practice
//! 
//! 1. Write formal specifications
//! 2. Verify spec completeness
//! 3. Generate tests from specs
//! 4. Implement to spec
//! 
//! ## Spec Document Structure
//! 
//! ```markdown
//! # Specification: Order Total Calculator
//! 
//! ## 1. Overview
//! Brief description of what this does.
//! 
//! ## 2. Functional Requirements
//! 
//! ### 2.1 REQ-001: Calculate order total
//! - Input: List of items with prices and quantities
//! - Output: Sum of (price * quantity) for all items
//! - Constraints:
//!   - Price must be non-negative
//!   - Quantity must be positive integer
//! 
//! ### 2.2 REQ-002: Apply discount
//! - Input: Total amount, discount percentage
//! - Output: Total with discount applied
//! - Constraints:
//!   - Discount must be 0-100%
//! 
//! ## 3. Non-Functional Requirements
//! - Performance: < 1ms for 1000 items
//! - Precision: 2 decimal places
//! 
//! ## 4. Acceptance Criteria
//! - [ ] 10 items at $10 each = $100
//! - [ ] 10% discount on $100 = $90
//! - [ ] Invalid discount throws error
//! ```

/// Requirement types
#[derive(Debug, Clone)]
pub enum RequirementType {
    /// Functional requirement
    Functional,
    /// Non-functional requirement
    NonFunctional,
    /// Business rule
    BusinessRule,
}

/// Requirement status
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum RequirementStatus {
    /// Requirement is complete
    Complete,
    /// Requirement is partially implemented
    Partial,
    /// Requirement is not implemented
    NotImplemented,
}

/// A single requirement
#[derive(Debug)]
pub struct Requirement {
    pub id: String,
    pub title: String,
    pub description: String,
    pub req_type: RequirementType,
    pub status: RequirementStatus,
    pub acceptance_criteria: Vec<String>,
}

impl Requirement {
    pub fn new(id: impl Into<String>, title: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            title: title.into(),
            description: String::new(),
            req_type: RequirementType::Functional,
            status: RequirementStatus::NotImplemented,
            acceptance_criteria: Vec::new(),
        }
    }
    
    pub fn description(mut self, desc: impl Into<String>) -> Self {
        self.description = desc.into();
        self
    }
    
    pub fn functional(mut self) -> Self {
        self.req_type = RequirementType::Functional;
        self
    }
    
    pub fn non_functional(mut self) -> Self {
        self.req_type = RequirementType::NonFunctional;
        self
    }
    
    pub fn acceptance_criteria(mut self, criteria: Vec<&str>) -> Self {
        self.acceptance_criteria = criteria.into_iter().map(|s| s.to_string()).collect();
        self
    }
    
    pub fn is_complete(&self) -> bool {
        self.status == RequirementStatus::Complete
    }
}

/// Specification document
#[derive(Debug)]
pub struct Specification {
    pub id: String,
    pub title: String,
    pub version: String,
    pub requirements: Vec<Requirement>,
}

impl Specification {
    pub fn new(id: impl Into<String>, title: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            title: title.into(),
            version: "1.0.0".into(),
            requirements: Vec::new(),
        }
    }
    
    pub fn version(mut self, version: impl Into<String>) -> Self {
        self.version = version.into();
        self
    }
    
    pub fn add_requirement(mut self, req: Requirement) -> Self {
        self.requirements.push(req);
        self
    }
    
    pub fn completeness_percentage(&self) -> f64 {
        if self.requirements.is_empty() {
            return 0.0;
        }
        let complete = self.requirements.iter().filter(|r| r.is_complete()).count();
        (complete as f64 / self.requirements.len() as f64) * 100.0
    }
}

/// Spec item for verification
#[derive(Debug)]
pub struct SpecItem {
    pub id: String,
    pub input: String,
    pub expected_output: String,
    pub verified: bool,
}
