// Auto-generated usage examples for information_life
// Source: generate-api-docs.py

import { InformationPersona, check_integrity, decode_persona, encode_persona } from "./information_life";

// Create a InformationPersona instance
const informationpersona = new InformationPersona("example_agent_id");
informationpersona.check_integrity();
informationpersona.decode_persona("example_encoded_data");
informationpersona.encode_persona();

// Call check_integrity
check_integrity(undefined as unknown as any);
// Call decode_persona
decode_persona(undefined as unknown as any, "example_encoded_data");
// Call encode_persona
encode_persona(undefined as unknown as any);
