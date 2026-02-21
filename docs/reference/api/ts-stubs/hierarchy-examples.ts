// Auto-generated usage examples for hierarchy
// Source: generate-api-docs.py

import { AgentTree, get, get_ancestors, get_children, get_descendants, get_parent, list_agents, register, to_dict } from "./hierarchy";

// Create a AgentTree instance
const agenttree = new AgentTree();
agenttree.get("example_name");
agenttree.get_ancestors("example_name");
agenttree.get_children("example_name");
agenttree.get_descendants("example_name");
agenttree.get_parent("example_name");
agenttree.list_agents();
agenttree.register(undefined as unknown as SmolAgent);
agenttree.to_dict();

// Call get
get(undefined as unknown as any, "example_name");
// Call get_ancestors
get_ancestors(undefined as unknown as any, "example_name");
// Call get_children
get_children(undefined as unknown as any, "example_name");
// Call get_descendants
get_descendants(undefined as unknown as any, "example_name");
// Call get_parent
get_parent(undefined as unknown as any, "example_name");
// Call list_agents
list_agents(undefined as unknown as any);
// Call register
register(undefined as unknown as any, undefined as unknown as SmolAgent);
// Call to_dict
to_dict(undefined as unknown as any);
