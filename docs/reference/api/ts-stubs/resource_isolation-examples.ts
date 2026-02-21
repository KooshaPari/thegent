// Auto-generated usage examples for resource_isolation
// Source: generate-api-docs.py

import { EnvIsolator, ResourceIsolator, allocate_ports, cleanup_agent, setup_agent_env, wrap_env } from "./resource_isolation";

// Create a EnvIsolator instance
const envisolator = new EnvIsolator();
envisolator.wrap_env("example_agent_id", undefined as unknown as Record<(str, str)>);

// Create a ResourceIsolator instance
const resourceisolator = new ResourceIsolator("example_base_tmp_dir");
resourceisolator.allocate_ports("example_agent_id", 0);
resourceisolator.cleanup_agent("example_agent_id");
resourceisolator.setup_agent_env("example_agent_id");

// Call allocate_ports
allocate_ports(undefined as unknown as any, "example_agent_id", 0);
// Call cleanup_agent
cleanup_agent(undefined as unknown as any, "example_agent_id");
// Call setup_agent_env
setup_agent_env(undefined as unknown as any, "example_agent_id");
// Call wrap_env
wrap_env("example_agent_id", undefined as unknown as Record<(str, str)>);
