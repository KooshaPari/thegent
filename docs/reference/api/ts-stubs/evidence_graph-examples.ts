// Auto-generated usage examples for evidence_graph
// Source: generate-api-docs.py

import { EvidenceGraph, add_link, bundle_evidence } from "./evidence_graph";

// Create a EvidenceGraph instance
const evidencegraph = new EvidenceGraph("example_session_dir");
evidencegraph.add_link("example_parent_id", "example_child_id");
evidencegraph.bundle_evidence("example_target_path");

// Call add_link
add_link(undefined as unknown as any, "example_parent_id", "example_child_id");
// Call bundle_evidence
bundle_evidence(undefined as unknown as any, "example_target_path");
