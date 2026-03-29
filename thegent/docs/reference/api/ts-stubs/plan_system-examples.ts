// Auto-generated usage examples for plan_system
// Source: generate-api-docs.py

import { PlanSystemIntegration, get_blocked_tasks, get_tasks_for_phase, update_task_status } from "./plan_system";

// Create a PlanSystemIntegration instance
const plansystemintegration = new PlanSystemIntegration(undefined as unknown as any, undefined as unknown as any);
plansystemintegration.get_blocked_tasks();
plansystemintegration.get_tasks_for_phase("example_phase");
plansystemintegration.update_task_status("example_task_id", "example_status");

// Call get_blocked_tasks
get_blocked_tasks(undefined as unknown as any);
// Call get_tasks_for_phase
get_tasks_for_phase(undefined as unknown as any, "example_phase");
// Call update_task_status
update_task_status(undefined as unknown as any, "example_task_id", "example_status");
