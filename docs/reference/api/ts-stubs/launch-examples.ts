// Auto-generated usage examples for launch
// Source: generate-api-docs.py

import { LaunchObserver, check_health, trigger_rollback } from "./launch";

// Create a LaunchObserver instance
const launchobserver = new LaunchObserver(undefined as unknown as ThegentSettings);
launchobserver.check_health();
launchobserver.trigger_rollback("example_reason");

// Call check_health
check_health(undefined as unknown as any);
// Call trigger_rollback
trigger_rollback(undefined as unknown as any, "example_reason");
