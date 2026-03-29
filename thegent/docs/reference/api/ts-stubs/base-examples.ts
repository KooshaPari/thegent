// Auto-generated usage examples for base
// Source: generate-api-docs.py

import { SmolAgent, SmolGentJob, SmolGentResult, add_tool, children, delegate, execute_job, get_tool, memory, parent, recall, remember, run, set_parent, tools } from "./base";

// Create a SmolAgent instance
const smolagent = new SmolAgent("example_name", undefined as unknown as Array<Tool>);
smolagent.add_tool(undefined as unknown as Tool);
smolagent.children();
smolagent.delegate(undefined as unknown as any);
smolagent.execute_job(undefined as unknown as SmolGentJob);
smolagent.get_tool("example_name");
smolagent.memory();
smolagent.parent();
smolagent.recall("example_key");
smolagent.remember("example_key", undefined as unknown as any);
smolagent.run(undefined as unknown as any);
smolagent.set_parent(undefined as unknown as SmolAgent);
smolagent.tools();

// Create a SmolGentJob instance
const smolgentjob = new SmolGentJob();

// Create a SmolGentResult instance
const smolgentresult = new SmolGentResult();

// Call add_tool
add_tool(undefined as unknown as any, undefined as unknown as Tool);
// Call children
children(undefined as unknown as any);
// Call delegate
delegate(undefined as unknown as any, undefined as unknown as any);
// Call execute_job
execute_job(undefined as unknown as any, undefined as unknown as SmolGentJob);
// Call get_tool
get_tool(undefined as unknown as any, "example_name");
// Call memory
memory(undefined as unknown as any);
// Call parent
parent(undefined as unknown as any);
// Call recall
recall(undefined as unknown as any, "example_key");
// Call remember
remember(undefined as unknown as any, "example_key", undefined as unknown as any);
// Call run
run(undefined as unknown as any, undefined as unknown as any);
// Call set_parent
set_parent(undefined as unknown as any, undefined as unknown as SmolAgent);
// Call tools
tools(undefined as unknown as any);
