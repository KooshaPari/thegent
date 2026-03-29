// Auto-generated usage examples for schema_formal
// Source: generate-api-docs.py

import { SchemaEvolutionVerifier, check_liveness_impact, verify_compatibility, verify_tag_evolution } from "./schema_formal";

// Create a SchemaEvolutionVerifier instance
const schemaevolutionverifier = new SchemaEvolutionVerifier();
schemaevolutionverifier.check_liveness_impact(undefined as unknown as Record<(str, Any)>);
schemaevolutionverifier.verify_compatibility(undefined as unknown as Record<(str, Any)>, undefined as unknown as Record<(str, Any)>);
schemaevolutionverifier.verify_tag_evolution(undefined as unknown as Array<string>, undefined as unknown as Array<string>);

// Call check_liveness_impact
check_liveness_impact(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call verify_compatibility
verify_compatibility(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, undefined as unknown as Record<(str, Any)>);
// Call verify_tag_evolution
verify_tag_evolution(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as Array<string>);
