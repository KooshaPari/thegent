// Auto-generated usage examples for observability_v2
// Source: generate-api-docs.py

import { AdvancedMetrics, JSONLFormatter, MeshCLI, format, record, status, tasks } from "./observability_v2";

// Create a AdvancedMetrics instance
const advancedmetrics = new AdvancedMetrics("example_metrics_file");
advancedmetrics.record("example_agent_id", "example_command", 0, false);

// Create a JSONLFormatter instance
const jsonlformatter = new JSONLFormatter();
jsonlformatter.format(undefined as unknown as any);

// Create a MeshCLI instance
const meshcli = new MeshCLI();
meshcli.status("example_mesh_dir");
meshcli.tasks("example_mesh_dir");

// Call format
format(undefined as unknown as any, undefined as unknown as any);
// Call record
record(undefined as unknown as any, "example_agent_id", "example_command", 0, false);
// Call status
status("example_mesh_dir");
// Call tasks
tasks("example_mesh_dir");
