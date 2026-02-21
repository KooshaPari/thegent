// Auto-generated usage examples for personas
// Source: generate-api-docs.py

import { PersonaManager, check_access, discover_teammates, list_teammates } from "./personas";

// Create a PersonaManager instance
const personamanager = new PersonaManager(undefined as unknown as any);
personamanager.check_access("example_persona", "example_operation", "example_lane");
personamanager.discover_teammates();
personamanager.list_teammates();

// Call check_access
check_access(undefined as unknown as any, "example_persona", "example_operation", "example_lane");
// Call discover_teammates
discover_teammates(undefined as unknown as any);
// Call list_teammates
list_teammates(undefined as unknown as any);
