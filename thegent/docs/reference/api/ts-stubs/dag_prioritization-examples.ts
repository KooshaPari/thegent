// Auto-generated usage examples for dag_prioritization
// Source: generate-api-docs.py

import { DagCycleError, DagPrioritizer, DagTask, add_task, compute_critical_path, get_priority_score, ready_tasks, topological_sort } from "./dag_prioritization";

// Create a DagCycleError instance
const dagcycleerror = new DagCycleError();

// Create a DagPrioritizer instance
const dagprioritizer = new DagPrioritizer();
dagprioritizer.add_task(undefined as unknown as DagTask);
dagprioritizer.compute_critical_path();
dagprioritizer.get_priority_score("example_task_id");
dagprioritizer.ready_tasks(undefined as unknown as set<string>);
dagprioritizer.topological_sort();

// Create a DagTask instance
const dagtask = new DagTask();

// Call add_task
add_task(undefined as unknown as any, undefined as unknown as DagTask);
// Call compute_critical_path
compute_critical_path(undefined as unknown as any);
// Call get_priority_score
get_priority_score(undefined as unknown as any, "example_task_id");
// Call ready_tasks
ready_tasks(undefined as unknown as any, undefined as unknown as set<string>);
// Call topological_sort
topological_sort(undefined as unknown as any);
