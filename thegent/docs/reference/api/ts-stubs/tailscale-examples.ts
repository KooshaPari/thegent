// Auto-generated usage examples for tailscale
// Source: generate-api-docs.py

import { TailscaleConfig, TailscaleError, TailscaleManager, TailscaleNode, get_online_nodes, is_available, list_nodes, ping_node } from "./tailscale";

// Create a TailscaleConfig instance
const tailscaleconfig = new TailscaleConfig();

// Create a TailscaleError instance
const tailscaleerror = new TailscaleError();

// Create a TailscaleManager instance
const tailscalemanager = new TailscaleManager(undefined as unknown as any);
tailscalemanager.get_online_nodes();
tailscalemanager.is_available();
tailscalemanager.list_nodes();
tailscalemanager.ping_node("example_hostname");

// Create a TailscaleNode instance
const tailscalenode = new TailscaleNode();

// Call get_online_nodes
get_online_nodes(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call list_nodes
list_nodes(undefined as unknown as any);
// Call ping_node
ping_node(undefined as unknown as any, "example_hostname");
