//! Task Graph Module
//!
//! Handles task definitions, dependency resolution, and topological sorting.

use std::collections::{HashMap, HashSet, VecDeque};
use std::fmt;

use crate::config::{ForgeConfig, TaskConfig};
use crate::{ForgeError, Result};

/// Unique identifier for a task
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct TaskId(String);

impl TaskId {
    pub fn new(name: impl Into<String>) -> Self {
        Self(name.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for TaskId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl PartialEq<&str> for TaskId {
    fn eq(&self, other: &&str) -> bool {
        self.0 == *other
    }
}

/// A task in the dependency graph
#[derive(Debug, Clone)]
pub struct Task {
    pub id: TaskId,
    pub command: String,
    pub description: Option<String>,
    pub dependencies: Vec<TaskId>,
    pub watch: Option<Vec<String>>,
}

impl Task {
    pub fn new(id: TaskId, config: TaskConfig) -> Self {
        Self {
            id,
            command: config.command,
            description: config.description,
            dependencies: config.dependencies.into_iter().map(TaskId::new).collect(),
            watch: config.watch,
        }
    }
}

/// Directed acyclic graph of tasks with dependency resolution
#[derive(Debug)]
pub struct TaskGraph {
    tasks: HashMap<TaskId, Task>,
    dependents: HashMap<TaskId, HashSet<TaskId>>,
}

impl TaskGraph {
    /// Build a task graph from configuration
    pub fn from_config(config: &ForgeConfig) -> Result<Self> {
        let mut tasks = HashMap::new();
        let mut dependents: HashMap<TaskId, HashSet<TaskId>> = HashMap::new();

        for (name, task_config) in &config.tasks {
            let id = TaskId::new(name);
            tasks.insert(id.clone(), Task::new(id.clone(), task_config.clone()));
            dependents.insert(id.clone(), HashSet::new());
        }

        for (id, task) in &tasks {
            for dep in &task.dependencies {
                dependents
                    .get_mut(dep)
                    .ok_or_else(|| ForgeError::TaskNotFound(dep.to_string()))?
                    .insert(id.clone());
            }
        }

        for (id, task) in &tasks {
            for dep in &task.dependencies {
                if !tasks.contains_key(dep) {
                    return Err(ForgeError::TaskNotFound(format!("{} (required by {})", dep, id)));
                }
            }
        }

        let graph = Self { tasks, dependents };
        graph.validate_acyclic()?;

        Ok(graph)
    }

    fn validate_acyclic(&self) -> Result<()> {
        let mut visited = HashSet::new();
        let mut stack = HashSet::new();

        for id in self.tasks.keys() {
            if !visited.contains(id) {
                if self.has_cycle_dfs(id, &mut visited, &mut stack) {
                    return Err(ForgeError::CircularDependency(id.to_string()));
                }
            }
        }

        Ok(())
    }

    fn has_cycle_dfs(&self, id: &TaskId, visited: &mut HashSet<TaskId>, stack: &mut HashSet<TaskId>) -> bool {
        visited.insert(id.clone());
        stack.insert(id.clone());

        if let Some(task) = self.tasks.get(id) {
            for dep in &task.dependencies {
                if !visited.contains(dep) {
                    if self.has_cycle_dfs(dep, visited, stack) {
                        return true;
                    }
                } else if stack.contains(dep) {
                    return true;
                }
            }
        }

        stack.remove(id);
        false
    }

    pub fn get(&self, id: &TaskId) -> Option<&Task> {
        self.tasks.get(id)
    }

    pub fn tasks(&self) -> &HashMap<TaskId, Task> {
        &self.tasks
    }

    pub fn dependencies(&self, id: &TaskId) -> Result<&Vec<TaskId>> {
        Ok(&self.tasks.get(id).ok_or_else(|| ForgeError::TaskNotFound(id.to_string()))?.dependencies)
    }

    pub fn dependents(&self, id: &TaskId) -> Option<&HashSet<TaskId>> {
        self.dependents.get(id)
    }

    /// Get execution order using topological sort (Kahn's algorithm)
    pub fn execution_order(&self) -> Vec<TaskId> {
        let mut in_degree: HashMap<TaskId, usize> = self.tasks.keys().map(|id| (id.clone(), 0)).collect();

        for task in self.tasks.values() {
            for dep in &task.dependencies {
                if let Some(deg) = in_degree.get_mut(dep) {
                    *deg += 1;
                }
            }
        }

        let mut queue: VecDeque<TaskId> = in_degree.iter().filter(|(_, &deg)| deg == 0).map(|(id, _)| id.clone()).collect();
        let mut result = Vec::new();

        while let Some(id) = queue.pop_front() {
            result.push(id.clone());

            if let Some(dependents) = self.dependents.get(&id) {
                for dependent in dependents {
                    if let Some(deg) = in_degree.get_mut(dependent) {
                        *deg -= 1;
                        if *deg == 0 {
                            queue.push_back(dependent.clone());
                        }
                    }
                }
            }
        }

        result
    }

    pub fn required_tasks(&self, targets: &[String]) -> Result<Vec<TaskId>> {
        let mut needed: HashSet<TaskId> = HashSet::new();
        let mut queue: VecDeque<TaskId> = targets.iter().map(|t| TaskId::new(t)).filter(|id| self.tasks.contains_key(id)).collect();

        while let Some(id) = queue.pop_front() {
            if needed.contains(&id) {
                continue;
            }
            needed.insert(id.clone());

            if let Ok(deps) = self.dependencies(&id) {
                for dep in deps {
                    if !needed.contains(dep) {
                        queue.push_back(dep.clone());
                    }
                }
            }
        }

        let mut result = Vec::new();
        let mut seen = HashSet::new();

        fn dfs(graph: &TaskGraph, id: &TaskId, needed: &HashSet<TaskId>, result: &mut Vec<TaskId>, seen: &mut HashSet<TaskId>) {
            if !needed.contains(id) || seen.contains(id) {
                return;
            }
            seen.insert(id.clone());

            if let Ok(deps) = graph.dependencies(id) {
                for dep in deps {
                    dfs(graph, dep, needed, result, seen);
                }
            }

            result.push(id.clone());
        }

        for target in targets {
            dfs(self, &TaskId::new(target), &needed, &mut result, &mut seen);
        }

        Ok(result)
    }

    pub fn dependents_transitive(&self, id: &TaskId) -> HashSet<TaskId> {
        let mut result = HashSet::new();
        let mut stack = vec![id.clone()];

        while let Some(current) = stack.pop() {
            if let Some(deps) = self.dependents.get(&current) {
                for dep in deps {
                    if result.insert(dep.clone()) {
                        stack.push(dep.clone());
                    }
                }
            }
        }

        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_simple_config() -> ForgeConfig {
        ForgeConfig {
            tasks: HashMap::from([
                ("a".to_string(), TaskConfig { command: "echo a".to_string(), dependencies: vec![], description: None, watch: None, env: Default::default(), timeout: 0 }),
                ("b".to_string(), TaskConfig { command: "echo b".to_string(), dependencies: vec!["a".to_string()], description: None, watch: None, env: Default::default(), timeout: 0 }),
                ("c".to_string(), TaskConfig { command: "echo c".to_string(), dependencies: vec!["a".to_string()], description: None, watch: None, env: Default::default(), timeout: 0 }),
                ("d".to_string(), TaskConfig { command: "echo d".to_string(), dependencies: vec!["b".to_string(), "c".to_string()], description: None, watch: None, env: Default::default(), timeout: 0 }),
            ]),
            workers: None,
            watch: vec![],
            env: Default::default(),
            ignore: vec![],
        }
    }

    #[test]
    fn test_execution_order() {
        let config = create_simple_config();
        let graph = TaskGraph::from_config(&config).unwrap();

        let order = graph.execution_order();
        assert_eq!(order.len(), 4);

        let a_idx = order.iter().position(|id| id.as_str() == "a").unwrap();
        let b_idx = order.iter().position(|id| id.as_str() == "b").unwrap();
        let c_idx = order.iter().position(|id| id.as_str() == "c").unwrap();
        let d_idx = order.iter().position(|id| id.as_str() == "d").unwrap();

        assert!(a_idx < b_idx);
        assert!(a_idx < c_idx);
        assert!(b_idx < d_idx);
        assert!(c_idx < d_idx);
    }

    #[test]
    fn test_required_tasks() {
        let config = create_simple_config();
        let graph = TaskGraph::from_config(&config).unwrap();

        let required = graph.required_tasks(&["d".to_string()]).unwrap();
        assert_eq!(required.len(), 4);
        assert!(required.contains(&TaskId::new("a")));
        assert!(required.contains(&TaskId::new("b")));
        assert!(required.contains(&TaskId::new("c")));
        assert!(required.contains(&TaskId::new("d")));
    }

    #[test]
    fn test_circular_dependency() {
        let mut config = create_simple_config();
        config.tasks.get_mut("a").unwrap().dependencies = vec!["d".to_string()];

        let result = TaskGraph::from_config(&config);
        assert!(matches!(result, Err(ForgeError::CircularDependency(_))));
    }
}
