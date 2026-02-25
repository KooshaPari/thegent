//! Python bindings for `thegent-hooks`.

use crate::changed_files::{ChangeStatus, ChangedFilesDetector, ChangedFile, FilterOptions, ImpactType};
use crate::config::ConfigLoader;
use crate::cost::CostCalculator;
use crate::policy::PolicyEngine;
use crate::quality::QualityEvaluator;
use crate::security::SecurityScanner;
use crate::types::{
    HookConfig, HookError, PolicyOutcome, PolicyRule, SecurityFinding, Severity as RustSeverity,
    RuleType as RustRuleType, CostEstimate, LintIssue,
};

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use serde_json::{Map, Value};
use std::collections::HashMap;
use std::collections::HashSet;

fn parse_context(context_json: &str) -> PyResult<HashMap<String, Value>> {
    let value: Value =
        serde_json::from_str(context_json).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let map = value.as_object().ok_or_else(|| {
        PyValueError::new_err("context_json must be a JSON object with policy context fields")
    })?;
    Ok(map.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
}

fn rust_rule_type(value: &str) -> PyResult<RustRuleType> {
    match value.to_lowercase().as_str() {
        "cost" => Ok(RustRuleType::Cost),
        "quality" => Ok(RustRuleType::Quality),
        "security" => Ok(RustRuleType::Security),
        "spec" => Ok(RustRuleType::Spec),
        other => Err(PyValueError::new_err(format!("invalid rule_type: {other}"))),
    }
}

fn rust_severity(value: &str) -> PyResult<RustSeverity> {
    match value.to_lowercase().as_str() {
        "info" => Ok(RustSeverity::Info),
        "warning" => Ok(RustSeverity::Warning),
        "error" => Ok(RustSeverity::Error),
        "critical" => Ok(RustSeverity::Critical),
        other => Err(PyValueError::new_err(format!("invalid severity: {other}"))),
    }
}

fn map_change_status(value: &str) -> PyResult<ChangeStatus> {
    match value.to_lowercase().as_str() {
        "modified" | "m" => Ok(ChangeStatus::Modified),
        "added" | "a" | "??" => Ok(ChangeStatus::Added),
        "deleted" | "d" => Ok(ChangeStatus::Deleted),
        "untracked" | "u" | "?" => Ok(ChangeStatus::Untracked),
        other => Err(PyValueError::new_err(format!("invalid change status: {other}"))),
    }
}

fn map_impact_type(value: &str) -> PyResult<ImpactType> {
    match value.to_lowercase().as_str() {
        "codeimpacting" | "code" => Ok(ImpactType::CodeImpacting),
        "docsonly" | "docs" => Ok(ImpactType::DocsOnly),
        "config" => Ok(ImpactType::Config),
        "tests" => Ok(ImpactType::Tests),
        "build" => Ok(ImpactType::Build),
        "other" => Ok(ImpactType::Other),
        other => Err(PyValueError::new_err(format!("invalid impact type: {other}"))),
    }
}

fn map_security_findings(input: Vec<SecurityFinding>) -> Vec<PySecurityFinding> {
    input
        .into_iter()
        .map(|finding| PySecurityFinding {
            id: finding.id,
            severity: format!("{:?}", finding.severity).to_lowercase(),
            category: finding.category,
            message: finding.message,
            location: finding.location,
            remediation: finding.remediation,
        })
        .collect()
}

#[pyclass(name = "PolicyRule")]
pub struct PyPolicyRule {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub description: String,
    #[pyo3(get)]
    pub rule_type: String,
    #[pyo3(get)]
    pub condition: String,
    #[pyo3(get)]
    pub severity: String,
    #[pyo3(get)]
    pub enabled: bool,
}

#[pymethods]
impl PyPolicyRule {
    #[new]
    fn new(
        id: String,
        name: String,
        description: String,
        rule_type: String,
        condition: String,
        severity: String,
        enabled: bool,
    ) -> PyResult<Self> {
        rust_rule_type(&rule_type)?;
        rust_severity(&severity)?;
        Ok(Self {
            id,
            name,
            description,
            rule_type,
            condition,
            severity,
            enabled,
        })
    }
}

#[pyclass(name = "PolicyOutcome")]
pub struct PyPolicyOutcome {
    #[pyo3(get)]
    pub rule_id: String,
    #[pyo3(get)]
    pub passed: bool,
    #[pyo3(get)]
    pub message: String,
    #[pyo3(get)]
    pub details: Option<String>,
}

impl From<PolicyOutcome> for PyPolicyOutcome {
    fn from(outcome: PolicyOutcome) -> Self {
        Self {
            rule_id: outcome.rule_id,
            passed: outcome.passed,
            message: outcome.message,
            details: outcome.details,
        }
    }
}

#[pyclass(name = "PolicyEngine")]
pub struct PyPolicyEngine {
    engine: PolicyEngine,
}

#[pymethods]
impl PyPolicyEngine {
    #[new]
    fn new(rules: Vec<PyPolicyRule>) -> PyResult<Self> {
        let rules = rules
            .into_iter()
            .map(|rule| {
                Ok(PolicyRule {
                    id: rule.id,
                    name: rule.name,
                    description: rule.description,
                    rule_type: rust_rule_type(&rule.rule_type)?,
                    condition: rule.condition,
                    severity: rust_severity(&rule.severity)?,
                    enabled: rule.enabled,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;

        Ok(Self {
            engine: PolicyEngine::new(rules),
        })
    }

    #[staticmethod]
    #[pyo3(signature = (config_path))]
    fn from_config(config_path: String) -> PyResult<Self> {
        let config: HookConfig = ConfigLoader::load(config_path.as_str())
            .map_err(|err: HookError| PyRuntimeError::new_err(err.to_string()))?;
        let rules = config
            .policies
            .into_iter()
            .map(|rule| PyPolicyRule {
                id: rule.id,
                name: rule.name,
                description: rule.description,
                rule_type: format!("{:?}", rule.rule_type).to_lowercase(),
                condition: rule.condition,
                severity: format!("{:?}", rule.severity).to_lowercase(),
                enabled: rule.enabled,
            })
            .collect();
        Self::new(rules)
    }

    fn evaluate(&self, context_json: String) -> PyResult<Vec<PyPolicyOutcome>> {
        let context = parse_context(&context_json)?;
        let outcomes = self
            .engine
            .evaluate(&context)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        Ok(outcomes.into_iter().map(PyPolicyOutcome::from).collect())
    }

    #[staticmethod]
    fn clear_cache() {
        PolicyEngine::clear_cache();
    }

    #[staticmethod]
    fn cache_stats(py: Python<'_>) -> PyResult<Py<PyAny>> {
        let (size, hits) = PolicyEngine::cache_stats();
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("cache_size", size)?;
        dict.set_item("cache_hits", hits)?;
        Ok(dict.into())
    }
}

#[pyclass(name = "CostEstimate")]
pub struct PyCostEstimate {
    #[pyo3(get)]
    pub model: String,
    #[pyo3(get)]
    pub input_tokens: u32,
    #[pyo3(get)]
    pub output_tokens: u32,
    #[pyo3(get)]
    pub input_cost_usd: f64,
    #[pyo3(get)]
    pub output_cost_usd: f64,
    #[pyo3(get)]
    pub total_cost_usd: f64,
}

impl From<CostEstimate> for PyCostEstimate {
    fn from(estimate: CostEstimate) -> Self {
        Self {
            model: estimate.model,
            input_tokens: estimate.input_tokens,
            output_tokens: estimate.output_tokens,
            input_cost_usd: estimate.input_cost_usd,
            output_cost_usd: estimate.output_cost_usd,
            total_cost_usd: estimate.total_cost_usd,
        }
    }
}

#[pyclass(name = "CostCalculator")]
pub struct PyCostCalculator {
    calculator: CostCalculator,
}

#[pymethods]
impl PyCostCalculator {
    #[new]
    fn new() -> Self {
        Self {
            calculator: CostCalculator::new(),
        }
    }

    fn calculate(&self, model: String, input_tokens: u32, output_tokens: u32) -> PyResult<PyCostEstimate> {
        let estimate = self
            .calculator
            .calculate(&model, input_tokens, output_tokens)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        Ok(PyCostEstimate::from(estimate))
    }

    fn add_model_pricing(
        &mut self,
        model: String,
        input_cost_per_mtok: f64,
        output_cost_per_mtok: f64,
    ) {
        self.calculator
            .add_model_pricing(&model, input_cost_per_mtok, output_cost_per_mtok)
    }

    fn known_models(&self) -> Vec<String> {
        self.calculator.known_models()
    }

    fn cost_to_value_ratio(&self, model: String, quality_score: f64) -> PyResult<f64> {
        self.calculator
            .cost_to_value_ratio(&model, quality_score)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))
    }
}

#[pyclass(name = "SecurityFinding")]
pub struct PySecurityFinding {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub severity: String,
    #[pyo3(get)]
    pub category: String,
    #[pyo3(get)]
    pub message: String,
    #[pyo3(get)]
    pub location: Option<String>,
    #[pyo3(get)]
    pub remediation: Option<String>,
}

#[pyclass(name = "SecurityScanner")]
pub struct PySecurityScanner {
    scanner: SecurityScanner,
}

#[pymethods]
impl PySecurityScanner {
    #[new]
    fn new() -> Self {
        Self {
            scanner: SecurityScanner::new(),
        }
    }

    fn scan_text(&self, content: String) -> Vec<PySecurityFinding> {
        map_security_findings(self.scanner.scan_text(&content))
    }

    fn parse_semgrep_json(&self, json_text: String) -> PyResult<Vec<PySecurityFinding>> {
        let findings = SecurityScanner::parse_semgrep_json(&json_text)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        Ok(map_security_findings(findings))
    }

    fn add_pattern(&mut self, name: String, pattern: String, severity: String) -> PyResult<()> {
        let severity = rust_severity(&severity)?;
        self.scanner
            .add_pattern(&name, &pattern, severity)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))
    }
}

#[pyclass(name = "ChangedFile")]
pub struct PyChangedFile {
    #[pyo3(get)]
    pub path: String,
    #[pyo3(get)]
    pub status: String,
    #[pyo3(get)]
    pub impact: String,
}

fn py_from_changed_file(file: ChangedFile) -> PyChangedFile {
    PyChangedFile {
        path: file.path.to_string_lossy().to_string(),
        status: format!("{:?}", file.status).to_lowercase(),
        impact: format!("{:?}", file.impact).to_lowercase(),
    }
}

#[pyclass(name = "ChangedFilesDetector")]
pub struct PyChangedFilesDetector {
    detector: ChangedFilesDetector,
}

#[pymethods]
impl PyChangedFilesDetector {
    #[new]
    fn new() -> PyResult<Self> {
        let detector = ChangedFilesDetector::new().map_err(|err| {
            PyRuntimeError::new_err(format!("failed to create changed files detector: {err}"))
        })?;
        Ok(Self { detector })
    }

    #[staticmethod]
    fn from_path(path: String) -> PyResult<Self> {
        let detector = ChangedFilesDetector::from_path(path).map_err(|err| {
            PyRuntimeError::new_err(format!("failed to create detector from path: {err}"))
        })?;
        Ok(Self { detector })
    }

    fn get_changed_files(&self, rev_range: Option<String>) -> PyResult<Vec<PyChangedFile>> {
        let files = self
            .detector
            .get_changed_files(rev_range.as_deref())
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        Ok(files.into_iter().map(py_from_changed_file).collect())
    }

    #[pyo3(signature = (rev_range=None, extensions=None, directories=None, statuses=None, impact_types=None, exclude_extensions=None, exclude_directories=None))]
    fn get_filtered(
        &self,
        rev_range: Option<String>,
        extensions: Option<Vec<String>>,
        directories: Option<Vec<String>>,
        statuses: Option<Vec<String>>,
        impact_types: Option<Vec<String>>,
        exclude_extensions: Option<Vec<String>>,
        exclude_directories: Option<Vec<String>>,
    ) -> PyResult<Vec<PyChangedFile>> {
        let mut filters = FilterOptions::default();

        if let Some(exts) = extensions {
            filters.extensions = exts;
        }
        if let Some(dirs) = directories {
            filters.directories = dirs;
        }
        if let Some(status_values) = statuses {
            let mut set = HashSet::new();
            for status in status_values {
                set.insert(map_change_status(&status)?);
            }
            filters.statuses = set.into_iter().collect();
        }
        if let Some(impact_values) = impact_types {
            let mut set = HashSet::new();
            for impact in impact_values {
                set.insert(map_impact_type(&impact)?);
            }
            filters.impact_types = set.into_iter().collect();
        }
        if let Some(values) = exclude_extensions {
            filters.exclude_extensions = values;
        }
        if let Some(values) = exclude_directories {
            filters.exclude_directories = values;
        }

        let files = self
            .detector
            .get_filtered(rev_range.as_deref(), filters)
            .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        Ok(files.into_iter().map(py_from_changed_file).collect())
    }
}

#[pyfunction]
#[pyo3(signature = (path))]
fn parse_hook_config(path: String) -> PyResult<PyPolicyRule> {
    let config = ConfigLoader::load(path).map_err(|err: HookError| {
        PyRuntimeError::new_err(format!("failed to load hook config: {err}"))
    })?;

    config
        .policies
        .into_iter()
        .next()
        .map(|rule| PyPolicyRule {
            id: rule.id,
            name: rule.name,
            description: rule.description,
            rule_type: format!("{:?}", rule.rule_type).to_lowercase(),
            condition: rule.condition,
            severity: format!("{:?}", rule.severity).to_lowercase(),
            enabled: rule.enabled,
        })
        .ok_or_else(|| PyRuntimeError::new_err("hook config contained no policy rules"))
}

#[pyfunction]
#[pyo3(signature = (json_text))]
fn parse_ruff_json(json_text: String) -> PyResult<Vec<String>> {
    let issues: Vec<LintIssue> = QualityEvaluator::parse_ruff_json(&json_text)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
    Ok(issues
        .into_iter()
        .map(|issue| {
            let mut map: Map<String, Value> = Map::new();
            map.insert("rule".to_string(), Value::String(issue.rule));
            map.insert("severity".to_string(), Value::String(issue.severity));
            map.insert("message".to_string(), Value::String(issue.message));
            if let Some(file) = issue.file {
                map.insert("file".to_string(), Value::String(file));
            }
            if let Some(line) = issue.line {
                map.insert("line".to_string(), Value::from(line));
            }
            if let Some(column) = issue.column {
                map.insert("column".to_string(), Value::from(column));
            }
            serde_json::to_string(&map).unwrap_or_else(|_| "{}".to_string())
        })
        .collect())
}

/// Python module for thegent-hooks.
#[pymodule]
fn thegent_hooks(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPolicyRule>()?;
    m.add_class::<PyPolicyOutcome>()?;
    m.add_class::<PyPolicyEngine>()?;
    m.add_class::<PyCostEstimate>()?;
    m.add_class::<PyCostCalculator>()?;
    m.add_class::<PySecurityFinding>()?;
    m.add_class::<PySecurityScanner>()?;
    m.add_class::<PyChangedFile>()?;
    m.add_class::<PyChangedFilesDetector>()?;

    m.add_function(wrap_pyfunction!(parse_hook_config, m)?)?;
    m.add_function(wrap_pyfunction!(parse_ruff_json, m)?)?;

    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
