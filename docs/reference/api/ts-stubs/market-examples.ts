// Auto-generated usage examples for market
// Source: generate-api-docs.py

import { AgentService, GlobalServiceRegistry, discover_services, list_service, run_auction } from "./market";

// Create a AgentService instance
const agentservice = new AgentService();

// Create a GlobalServiceRegistry instance
const globalserviceregistry = new GlobalServiceRegistry("example_storage_path");
globalserviceregistry.discover_services("example_capability");
globalserviceregistry.list_service(undefined as unknown as AgentService);
globalserviceregistry.run_auction("example_task_id", "example_capability", 0);

// Call discover_services
discover_services(undefined as unknown as any, "example_capability");
// Call list_service
list_service(undefined as unknown as any, undefined as unknown as AgentService);
// Call run_auction
run_auction(undefined as unknown as any, "example_task_id", "example_capability", 0);
