//! Behavior-Driven Development (BDD)
//! 
//! BDD extends TDD by using natural language descriptions of user scenarios.
//! Scenarios follow the Given-When-Then format.
//! 
//! ## Scenario Format
//! 
//! ```gherkin
//! Feature: Order Discounts
//! 
//!   Scenario: Calculate discount when quantity exceeds threshold
//!     Given an order with 10 items
//!     And a discount threshold of 5 items
//!     When I apply a 10% discount
//!     Then the total should be reduced by 10%
//! 
//!   Scenario: No discount when below threshold
//!     Given an order with 3 items
//!     And a discount threshold of 5 items
//!     When I apply a 10% discount
//!     Then no discount is applied
//! ```
//! 
//! ## Benefits
//! 
//! - Human-readable specifications
//! - Bridge between business and technical
//! - Living documentation
//! - Executable specifications

/// Scenario step types
#[derive(Debug, Clone, Copy)]
pub enum StepType {
    Given,
    When,
    Then,
    And,
    But,
}

/// Scenario step
#[derive(Debug)]
pub struct Step {
    pub step_type: StepType,
    pub text: String,
}

/// BDD Scenario
#[derive(Debug)]
pub struct Scenario {
    pub name: String,
    pub steps: Vec<Step>,
    pub tags: Vec<String>,
}

impl Scenario {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            steps: Vec::new(),
            tags: Vec::new(),
        }
    }
    
    pub fn given(mut self, text: impl Into<String>) -> Self {
        self.steps.push(Step {
            step_type: StepType::Given,
            text: text.into(),
        });
        self
    }
    
    pub fn when(mut self, text: impl Into<String>) -> Self {
        self.steps.push(Step {
            step_type: StepType::When,
            text: text.into(),
        });
        self
    }
    
    pub fn then(mut self, text: impl Into<String>) -> Self {
        self.steps.push(Step {
            step_type: StepType::Then,
            text: text.into(),
        });
        self
    }
    
    pub fn and(mut self, text: impl Into<String>) -> Self {
        self.steps.push(Step {
            step_type: StepType::And,
            text: text.into(),
        });
        self
    }
    
    pub fn with_tags(mut self, tags: Vec<&str>) -> Self {
        self.tags = tags.into_iter().map(|s| s.to_string()).collect();
        self
    }
}

/// BDD Feature
#[derive(Debug)]
pub struct Feature {
    pub name: String,
    pub description: String,
    pub scenarios: Vec<Scenario>,
    pub tags: Vec<String>,
}

impl Feature {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            description: String::new(),
            scenarios: Vec::new(),
            tags: Vec::new(),
        }
    }
    
    pub fn description(mut self, desc: impl Into<String>) -> Self {
        self.description = desc.into();
        self
    }
    
    pub fn scenario(mut self, scenario: Scenario) -> Self {
        self.scenarios.push(scenario);
        self
    }
    
    pub fn with_tags(mut self, tags: Vec<&str>) -> Self {
        self.tags = tags.into_iter().map(|s| s.to_string()).collect();
        self
    }
}

/// Gherkin parser for BDD scenarios
pub mod parser {
    use super::*;
    
    /// Parse a Gherkin feature file
    pub fn parse_feature(content: &str) -> Feature {
        let mut feature = Feature::new("Parsed Feature");
        let mut current_scenario: Option<Scenario> = None;
        
        for line in content.lines() {
            let line = line.trim();
            
            if line.starts_with("Feature:") {
                feature.name = line.trim_start_matches("Feature:").trim().to_string();
            } else if line.starts_with("Scenario:") {
                if let Some(scenario) = current_scenario.take() {
                    feature.scenarios.push(scenario);
                }
                current_scenario = Some(Scenario::new(line.trim_start_matches("Scenario:").trim()));
            } else if let Some(ref mut scenario) = current_scenario {
                if line.starts_with("Given ") {
                    scenario.given(line.trim_start_matches("Given ").trim());
                } else if line.starts_with("When ") {
                    scenario.when(line.trim_start_matches("When ").trim());
                } else if line.starts_with("Then ") {
                    scenario.then(line.trim_start_matches("Then ").trim());
                } else if line.starts_with("And ") {
                    scenario.and(line.trim_start_matches("And ").trim());
                }
            }
        }
        
        if let Some(scenario) = current_scenario {
            feature.scenarios.push(scenario);
        }
        
        feature
    }
    
    /// Convert feature to Gherkin format
    pub fn to_gherkin(feature: &Feature) -> String {
        let mut output = format!("Feature: {}\n\n", feature.name);
        
        if !feature.description.is_empty() {
            output.push_str(&format!("{}\n\n", feature.description));
        }
        
        for scenario in &feature.scenarios {
            output.push_str(&format!("  Scenario: {}\n", scenario.name));
            for step in &scenario.steps {
                let prefix = match step.step_type {
                    StepType::Given => "Given",
                    StepType::When => "When",
                    StepType::Then => "Then",
                    StepType::And => "And",
                    StepType::But => "But",
                };
                output.push_str(&format!("    {} {}\n", prefix, step.text));
            }
            output.push('\n');
        }
        
        output
    }
}
