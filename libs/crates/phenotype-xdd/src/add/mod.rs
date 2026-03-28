//! Attribute-Driven Design (ADD)
//! 
//! ADD is a software design methodology that focuses on identifying
//! quality attributes (non-functional requirements) and designing
//! the architecture around them.
//! 
//! ## ADD Steps
//! 
//! 1. **Choose architecturally significant requirements**
//!    - Identify quality attribute scenarios
//!    - Prioritize by business value and risk
//! 
//! 2. **Create candidate architectures**
//!    - Generate design alternatives
//!    - Evaluate against quality attributes
//! 
//! 3. **Evaluate candidates**
//!    - Analyze trade-offs
//!    - Select best option
//! 
//! 4. **Document the architecture**
//!    - Record design decisions
//!    - Create ADRs

/// Quality attribute types
#[derive(Debug, Clone)]
pub enum QualityAttribute {
    /// Performance (latency, throughput)
    Performance,
    /// Availability (uptime, failover)
    Availability,
    /// Security (confidentiality, integrity)
    Security,
    /// Modifiability (maintainability, extensibility)
    Modifiability,
    /// Testability
    Testability,
    /// Scalability
    Scalability,
    /// Reliability
    Reliability,
    /// Deployability
    Deployability,
}

/// Quality attribute scenario
#[derive(Debug)]
pub struct QAScenario {
    /// Source of stimulus (user, system, attacker)
    pub source: String,
    /// Stimulus that triggers the system
    pub stimulus: String,
    /// Artifact affected
    pub artifact: String,
    /// Environment in which stimulus occurs
    pub environment: String,
    /// Response to stimulus
    pub response: String,
    /// How to measure the response
    pub response_measure: String,
}

impl QAScenario {
    pub fn new(
        source: impl Into<String>,
        stimulus: impl Into<String>,
    ) -> Self {
        Self {
            source: source.into(),
            stimulus: stimulus.into(),
            artifact: String::new(),
            environment: String::new(),
            response: String::new(),
            response_measure: String::new(),
        }
    }
    
    pub fn affecting(mut self, artifact: impl Into<String>) -> Self {
        self.artifact = artifact.into();
        self
    }
    
    pub fn in_environment(mut self, env: impl Into<String>) -> Self {
        self.environment = env.into();
        self
    }
    
    pub fn system_should(mut self, response: impl Into<String>) -> Self {
        self.response = response.into();
        self
    }
    
    pub fn measured_by(mut self, measure: impl Into<String>) -> Self {
        self.response_measure = measure.into();
        self
    }
}

/// Design decision
#[derive(Debug)]
pub struct DesignDecision {
    pub id: String,
    pub title: String,
    pub attribute: QualityAttribute,
    pub decision: String,
    pub rationale: String,
    pub alternatives: Vec<String>,
}

impl DesignDecision {
    pub fn new(
        id: impl Into<String>,
        title: impl Into<String>,
        attribute: QualityAttribute,
    ) -> Self {
        Self {
            id: id.into(),
            title: title.into(),
            attribute,
            decision: String::new(),
            rationale: String::new(),
            alternatives: Vec::new(),
        }
    }
    
    pub fn decision(mut self, decision: impl Into<String>) -> Self {
        self.decision = decision.into();
        self
    }
    
    pub fn rationale(mut self, rationale: impl Into<String>) -> Self {
        self.rationale = rationale.into();
        self
    }
    
    pub fn consider_alternatives(mut self, alts: Vec<&str>) -> Self {
        self.alternatives = alts.into_iter().map(|s| s.to_string()).collect();
        self
    }
}
