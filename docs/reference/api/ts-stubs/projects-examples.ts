// Auto-generated usage examples for projects
// Source: generate-api-docs.py

import { ContextBridger, ProjectRegistry, get_peer_context, list_projects, register_project, update_activity } from "./projects";

// Create a ContextBridger instance
const contextbridger = new ContextBridger(undefined as unknown as ProjectRegistry);
contextbridger.get_peer_context("example_project_name", "example_file_pattern");

// Create a ProjectRegistry instance
const projectregistry = new ProjectRegistry("example_global_config_dir");
projectregistry.list_projects();
projectregistry.register_project("example_path", "example_name");
projectregistry.update_activity("example_path");

// Call get_peer_context
get_peer_context(undefined as unknown as any, "example_project_name", "example_file_pattern");
// Call list_projects
list_projects(undefined as unknown as any);
// Call register_project
register_project(undefined as unknown as any, "example_path", "example_name");
// Call update_activity
update_activity(undefined as unknown as any, "example_path");
