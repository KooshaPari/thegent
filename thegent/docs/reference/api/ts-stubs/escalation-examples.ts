// Auto-generated usage examples for escalation
// Source: generate-api-docs.py

import { EscalationItem, EscalationPriority, EscalationQueue, EscalationStatus, add, escalate, from_dict, get_item, list_items, resolve, to_dict } from "./escalation";

// Create a EscalationItem instance
const escalationitem = new EscalationItem();
escalationitem.from_dict(undefined as unknown as Record<(str, Any)>);
escalationitem.to_dict();

// Create a EscalationPriority instance
const escalationpriority = new EscalationPriority();

// Create a EscalationQueue instance
const escalationqueue = new EscalationQueue(undefined as unknown as any);
escalationqueue.add("example_run_id", "example_reason", 0);
escalationqueue.escalate("example_run_id", "example_prompt", "example_reason", "example_agent", undefined as unknown as EscalationPriority, 0, undefined as unknown as any);
escalationqueue.get_item("example_esc_id");
escalationqueue.list_items(undefined as unknown as any);
escalationqueue.resolve("example_esc_id", "example_resolution", "example_solver");

// Create a EscalationStatus instance
const escalationstatus = new EscalationStatus();

// Call add
add(undefined as unknown as any, "example_run_id", "example_reason", 0);
// Call escalate
escalate(undefined as unknown as any, "example_run_id", "example_prompt", "example_reason", "example_agent", undefined as unknown as EscalationPriority, 0, undefined as unknown as any);
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_item
get_item(undefined as unknown as any, "example_esc_id");
// Call list_items
list_items(undefined as unknown as any, undefined as unknown as any);
// Call resolve
resolve(undefined as unknown as any, "example_esc_id", "example_resolution", "example_solver");
// Call to_dict
to_dict(undefined as unknown as any);
