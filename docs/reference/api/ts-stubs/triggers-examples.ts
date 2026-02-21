// Auto-generated usage examples for triggers
// Source: generate-api-docs.py

import { HealthThresholdTrigger, ManualTrigger, TimerTrigger, TriggerConfig, TriggerProtocol, WatchdogTrigger, _WatchdogEventHandler, cli, create_trigger, main, monitor, on_created, on_deleted, on_modified, run, shutdown, start, stop, watch_filter } from "./triggers";

// Create a HealthThresholdTrigger instance
const healththresholdtrigger = new HealthThresholdTrigger(undefined as unknown as any, 0, 0);
healththresholdtrigger.start();
healththresholdtrigger.stop();

// Create a ManualTrigger instance
const manualtrigger = new ManualTrigger(undefined as unknown as any);
manualtrigger.run(false);

// Create a TimerTrigger instance
const timertrigger = new TimerTrigger(undefined as unknown as any, undefined as unknown as TriggerConfig);
timertrigger.start();
timertrigger.stop();

// Create a TriggerConfig instance
const triggerconfig = new TriggerConfig();

// Create a TriggerProtocol instance
const triggerprotocol = new TriggerProtocol();
triggerprotocol.start();
triggerprotocol.stop();

// Create a WatchdogTrigger instance
const watchdogtrigger = new WatchdogTrigger(undefined as unknown as any, undefined as unknown as TriggerConfig);
watchdogtrigger.start();
watchdogtrigger.stop();

// Create a _WatchdogEventHandler instance
const _watchdogeventhandler = new _WatchdogEventHandler(undefined as unknown as any, undefined as unknown as frozenset<string>, undefined as unknown as frozenset<string>);
_watchdogeventhandler.on_created(undefined as unknown as any);
_watchdogeventhandler.on_deleted(undefined as unknown as any);
_watchdogeventhandler.on_modified(undefined as unknown as any);

// Call cli
cli("example_mode", 0, 0, undefined as unknown as any, false, undefined as unknown as any, "example_project_dir", undefined as unknown as any, 0, "example_lifecycle_mode", 0, 0);
// Call create_trigger
create_trigger("example_mode", undefined as unknown as any, undefined as unknown as TriggerConfig);
// Call main
main();
// Call monitor
monitor();
// Call on_created
on_created(undefined as unknown as any, undefined as unknown as any);
// Call on_deleted
on_deleted(undefined as unknown as any, undefined as unknown as any);
// Call on_modified
on_modified(undefined as unknown as any, undefined as unknown as any);
// Call run
run(undefined as unknown as any, false);
// Call shutdown
shutdown(0, undefined as unknown as any);
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call watch_filter
watch_filter(undefined as unknown as Change, "example_path_str");
