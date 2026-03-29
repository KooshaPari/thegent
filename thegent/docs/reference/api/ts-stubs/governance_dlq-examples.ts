// Auto-generated usage examples for governance_dlq
// Source: generate-api-docs.py

import { EscalationQueueDLQ, enqueue, move_to_dlq, process } from "./governance_dlq";

// Create a EscalationQueueDLQ instance
const escalationqueuedlq = new EscalationQueueDLQ();
escalationqueuedlq.enqueue(undefined as unknown as Record<(str, Any)>);
escalationqueuedlq.move_to_dlq(undefined as unknown as Record<(str, Any)>, "example_reason");
escalationqueuedlq.process();

// Call enqueue
enqueue(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call move_to_dlq
move_to_dlq(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, "example_reason");
// Call process
process(undefined as unknown as any);
