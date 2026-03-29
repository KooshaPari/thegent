// Auto-generated usage examples for override_expired
// Source: generate-api-docs.py

import { OverrideExpirationHandler, check_expired, emit_expired_event, register_override } from "./override_expired";

// Create a OverrideExpirationHandler instance
const overrideexpirationhandler = new OverrideExpirationHandler();
overrideexpirationhandler.check_expired();
overrideexpirationhandler.emit_expired_event(undefined as unknown as Record<(str, Any)>);
overrideexpirationhandler.register_override("example_override_id", undefined as unknown as datetime, "example_policy");

// Call check_expired
check_expired(undefined as unknown as any);
// Call emit_expired_event
emit_expired_event(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call register_override
register_override(undefined as unknown as any, "example_override_id", undefined as unknown as datetime, "example_policy");
