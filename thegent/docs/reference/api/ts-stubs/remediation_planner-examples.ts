// Auto-generated usage examples for remediation_planner
// Source: generate-api-docs.py

import { Finding, RemediationPlan, RemediationPlanner, RemediationTask, plan } from "./remediation_planner";

// Create a Finding instance
const finding = new Finding();

// Create a RemediationPlan instance
const remediationplan = new RemediationPlan();

// Create a RemediationPlanner instance
const remediationplanner = new RemediationPlanner("example_health_targets_path");
remediationplanner.plan(undefined as unknown as Array<Finding>, 0);

// Create a RemediationTask instance
const remediationtask = new RemediationTask();

// Call plan
plan(undefined as unknown as any, undefined as unknown as Array<Finding>, 0);
