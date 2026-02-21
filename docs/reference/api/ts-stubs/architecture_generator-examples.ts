// Auto-generated usage examples for architecture_generator
// Source: generate-api-docs.py

import { ArchitectureGenerator, add_nodes, analyze_structure, generate_mermaid } from "./architecture_generator";

// Create a ArchitectureGenerator instance
const architecturegenerator = new ArchitectureGenerator();
architecturegenerator.analyze_structure("example_root_path");
architecturegenerator.generate_mermaid(undefined as unknown as Record<(str, Any)>);

// Call add_nodes
add_nodes(undefined as unknown as Record<(str, Any)>, "example_prefix");
// Call analyze_structure
analyze_structure(undefined as unknown as any, "example_root_path");
// Call generate_mermaid
generate_mermaid(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
