// Auto-generated usage examples for event_system
// Source: generate-api-docs.py

import { EventSystem, emit, subscribe } from "./event_system";

// Create a EventSystem instance
const eventsystem = new EventSystem();
eventsystem.emit("example_event_type", undefined as unknown as any);
eventsystem.subscribe("example_event_type", undefined as unknown as Callable);

// Call emit
emit(undefined as unknown as any, "example_event_type", undefined as unknown as any);
// Call subscribe
subscribe(undefined as unknown as any, "example_event_type", undefined as unknown as Callable);
