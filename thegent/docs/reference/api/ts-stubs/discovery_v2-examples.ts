// Auto-generated usage examples for discovery_v2
// Source: generate-api-docs.py

import { AgentManifest, AgentScanner, HeartbeatMonitor, beat, cleanup_stale, create, get_stale_agents, scan } from "./discovery_v2";

// Create a AgentManifest instance
const agentmanifest = new AgentManifest();
agentmanifest.create("example_manifest_path", undefined as unknown as Record<(str, Any)>);

// Create a AgentScanner instance
const agentscanner = new AgentScanner();
agentscanner.scan();

// Create a HeartbeatMonitor instance
const heartbeatmonitor = new HeartbeatMonitor("example_heartbeat_dir", 0);
heartbeatmonitor.beat("example_agent_id");
heartbeatmonitor.cleanup_stale(undefined as unknown as any);
heartbeatmonitor.get_stale_agents();

// Call beat
beat(undefined as unknown as any, "example_agent_id");
// Call cleanup_stale
cleanup_stale(undefined as unknown as any, undefined as unknown as any);
// Call create
create("example_manifest_path", undefined as unknown as Record<(str, Any)>);
// Call get_stale_agents
get_stale_agents(undefined as unknown as any);
// Call scan
scan(undefined as unknown as any);
