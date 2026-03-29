// Auto-generated usage examples for agent_hierarchy
// Source: generate-api-docs.py

import { AgentHierarchyManager, AgentNode, AgentRelationship, AgentRole, AgentTeam, CoordinationMode, RelationshipType, TeamType, add_team_member, build_tree, can_delegate, check_team_consistency, collect_descendants, create_relationship, create_team, detect_circular_relationships, detect_orphaned_agents, dfs, from_dict, get_agent, get_ancestors, get_children, get_descendants, get_hierarchy_tree, get_team, get_team_members, list_all_agents, list_all_relationships, list_all_teams, register_agent, remove_team_member, to_dict, update_agent_status, update_team_status, validate_agent_id, validate_before_register } from "./agent_hierarchy";

// Create a AgentHierarchyManager instance
const agenthierarchymanager = new AgentHierarchyManager("example_storage_path");
agenthierarchymanager.add_team_member("example_team_id", "example_agent_run_id");
agenthierarchymanager.can_delegate("example_from_agent_id", "example_to_agent_id", undefined as unknown as any);
agenthierarchymanager.check_team_consistency();
agenthierarchymanager.create_relationship("example_parent_id", "example_child_id", undefined as unknown as RelationshipType, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
agenthierarchymanager.create_team("example_team_id", "example_name", "example_description", undefined as unknown as TeamType, undefined as unknown as CoordinationMode, "example_lead_id", undefined as unknown as any, undefined as unknown as any);
agenthierarchymanager.detect_circular_relationships("example_start_id");
agenthierarchymanager.detect_orphaned_agents();
agenthierarchymanager.get_agent("example_run_id");
agenthierarchymanager.get_ancestors("example_agent_id");
agenthierarchymanager.get_children("example_parent_id");
agenthierarchymanager.get_descendants("example_agent_id");
agenthierarchymanager.get_hierarchy_tree(undefined as unknown as any);
agenthierarchymanager.get_team("example_team_id");
agenthierarchymanager.get_team_members("example_team_id");
agenthierarchymanager.list_all_agents();
agenthierarchymanager.list_all_relationships();
agenthierarchymanager.list_all_teams();
agenthierarchymanager.register_agent("example_agent_id", "example_run_id", undefined as unknown as AgentRole, undefined as unknown as any, undefined as unknown as any, false);
agenthierarchymanager.remove_team_member("example_team_id", "example_agent_run_id");
agenthierarchymanager.update_agent_status("example_run_id", "example_status");
agenthierarchymanager.update_team_status("example_team_id", "example_status");
agenthierarchymanager.validate_agent_id("example_agent_id");
agenthierarchymanager.validate_before_register("example_agent_id", "example_run_id", undefined as unknown as any, undefined as unknown as any);

// Create a AgentNode instance
const agentnode = new AgentNode();
agentnode.from_dict(undefined as unknown as Record<(str, Any)>);
agentnode.to_dict();

// Create a AgentRelationship instance
const agentrelationship = new AgentRelationship();
agentrelationship.from_dict(undefined as unknown as Record<(str, Any)>);
agentrelationship.to_dict();

// Create a AgentRole instance
const agentrole = new AgentRole();

// Create a AgentTeam instance
const agentteam = new AgentTeam();
agentteam.from_dict(undefined as unknown as Record<(str, Any)>);
agentteam.to_dict();

// Create a CoordinationMode instance
const coordinationmode = new CoordinationMode();

// Create a RelationshipType instance
const relationshiptype = new RelationshipType();

// Create a TeamType instance
const teamtype = new TeamType();

// Call add_team_member
add_team_member(undefined as unknown as any, "example_team_id", "example_agent_run_id");
// Call build_tree
build_tree(undefined as unknown as AgentNode);
// Call can_delegate
can_delegate(undefined as unknown as any, "example_from_agent_id", "example_to_agent_id", undefined as unknown as any);
// Call check_team_consistency
check_team_consistency(undefined as unknown as any);
// Call collect_descendants
collect_descendants(undefined as unknown as AgentNode);
// Call create_relationship
create_relationship(undefined as unknown as any, "example_parent_id", "example_child_id", undefined as unknown as RelationshipType, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call create_team
create_team(undefined as unknown as any, "example_team_id", "example_name", "example_description", undefined as unknown as TeamType, undefined as unknown as CoordinationMode, "example_lead_id", undefined as unknown as any, undefined as unknown as any);
// Call detect_circular_relationships
detect_circular_relationships(undefined as unknown as any, "example_start_id");
// Call detect_orphaned_agents
detect_orphaned_agents(undefined as unknown as any);
// Call dfs
dfs("example_node_id");
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_agent
get_agent(undefined as unknown as any, "example_run_id");
// Call get_ancestors
get_ancestors(undefined as unknown as any, "example_agent_id");
// Call get_children
get_children(undefined as unknown as any, "example_parent_id");
// Call get_descendants
get_descendants(undefined as unknown as any, "example_agent_id");
// Call get_hierarchy_tree
get_hierarchy_tree(undefined as unknown as any, undefined as unknown as any);
// Call get_team
get_team(undefined as unknown as any, "example_team_id");
// Call get_team_members
get_team_members(undefined as unknown as any, "example_team_id");
// Call list_all_agents
list_all_agents(undefined as unknown as any);
// Call list_all_relationships
list_all_relationships(undefined as unknown as any);
// Call list_all_teams
list_all_teams(undefined as unknown as any);
// Call register_agent
register_agent(undefined as unknown as any, "example_agent_id", "example_run_id", undefined as unknown as AgentRole, undefined as unknown as any, undefined as unknown as any, false);
// Call remove_team_member
remove_team_member(undefined as unknown as any, "example_team_id", "example_agent_run_id");
// Call to_dict
to_dict(undefined as unknown as any);
// Call update_agent_status
update_agent_status(undefined as unknown as any, "example_run_id", "example_status");
// Call update_team_status
update_team_status(undefined as unknown as any, "example_team_id", "example_status");
// Call validate_agent_id
validate_agent_id(undefined as unknown as any, "example_agent_id");
// Call validate_before_register
validate_before_register(undefined as unknown as any, "example_agent_id", "example_run_id", undefined as unknown as any, undefined as unknown as any);
