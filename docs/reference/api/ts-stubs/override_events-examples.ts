// Auto-generated usage examples for override_events
// Source: generate-api-docs.py

import { OverrideActivatedEvent, OverrideEventEmitter, OverrideExpiredEvent, OverrideExpiryMonitor, _Registration, emit_activated, emit_expired, register, start, stop, tail_events, to_dict, unregister } from "./override_events";

// Create a OverrideActivatedEvent instance
const overrideactivatedevent = new OverrideActivatedEvent();
overrideactivatedevent.to_dict();

// Create a OverrideEventEmitter instance
const overrideeventemitter = new OverrideEventEmitter(undefined as unknown as any);
overrideeventemitter.emit_activated("example_override_id", "example_policy_id", "example_owner", 0);
overrideeventemitter.emit_expired(undefined as unknown as OverrideExpiredEvent);
overrideeventemitter.tail_events(0);

// Create a OverrideExpiredEvent instance
const overrideexpiredevent = new OverrideExpiredEvent();
overrideexpiredevent.to_dict();

// Create a OverrideExpiryMonitor instance
const overrideexpirymonitor = new OverrideExpiryMonitor(undefined as unknown as any, 0);
overrideexpirymonitor.register("example_override_id", 0, undefined as unknown as Callable<(Any, None)>, "example_policy_id", "example_owner");
overrideexpirymonitor.start();
overrideexpirymonitor.stop(0);
overrideexpirymonitor.unregister("example_override_id");

// Create a _Registration instance
const _registration = new _Registration();

// Call emit_activated
emit_activated(undefined as unknown as any, "example_override_id", "example_policy_id", "example_owner", 0);
// Call emit_expired
emit_expired(undefined as unknown as any, undefined as unknown as OverrideExpiredEvent);
// Call register
register(undefined as unknown as any, "example_override_id", 0, undefined as unknown as Callable<(Any, None)>, "example_policy_id", "example_owner");
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any, 0);
// Call tail_events
tail_events(undefined as unknown as any, 0);
// Call to_dict
to_dict(undefined as unknown as any);
// Call unregister
unregister(undefined as unknown as any, "example_override_id");
