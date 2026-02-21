// Auto-generated usage examples for galactic
// Source: generate-api-docs.py

import { Bundle, DTNBridge, add_contact, process_contacts, send_bundle } from "./galactic";

// Create a Bundle instance
const bundle = new Bundle();

// Create a DTNBridge instance
const dtnbridge = new DTNBridge("example_node_id");
dtnbridge.add_contact("example_node_id", 0);
dtnbridge.process_contacts();
dtnbridge.send_bundle("example_dest_node", undefined as unknown as Uint8Array);

// Call add_contact
add_contact(undefined as unknown as any, "example_node_id", 0);
// Call process_contacts
process_contacts(undefined as unknown as any);
// Call send_bundle
send_bundle(undefined as unknown as any, "example_dest_node", undefined as unknown as Uint8Array);
