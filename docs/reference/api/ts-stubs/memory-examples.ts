// Auto-generated usage examples for memory
// Source: generate-api-docs.py

import { FrictionScope, MemoryCategory, MemoryFragment, MemorySystem, get_recent, record, synthesize_to_markdown } from "./memory";

// Create a FrictionScope instance
const frictionscope = new FrictionScope();

// Create a MemoryCategory instance
const memorycategory = new MemoryCategory();

// Create a MemoryFragment instance
const memoryfragment = new MemoryFragment();

// Create a MemorySystem instance
const memorysystem = new MemorySystem("example_project_root");
memorysystem.get_recent(0, undefined as unknown as any);
memorysystem.record("example_content", undefined as unknown as MemoryCategory, "example_agent_id", undefined as unknown as any, undefined as unknown as any);
memorysystem.synthesize_to_markdown();

// Call get_recent
get_recent(undefined as unknown as any, 0, undefined as unknown as any);
// Call record
record(undefined as unknown as any, "example_content", undefined as unknown as MemoryCategory, "example_agent_id", undefined as unknown as any, undefined as unknown as any);
// Call synthesize_to_markdown
synthesize_to_markdown(undefined as unknown as any);
