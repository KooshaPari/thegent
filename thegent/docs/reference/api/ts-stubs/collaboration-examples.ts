// Auto-generated usage examples for collaboration
// Source: generate-api-docs.py

import { CollaborativeSession, broadcast_state, recruit_participants } from "./collaboration";

// Create a CollaborativeSession instance
const collaborativesession = new CollaborativeSession(undefined as unknown as ThegentSettings, "example_task_id");
collaborativesession.broadcast_state(undefined as unknown as Record<(str, Any)>);
collaborativesession.recruit_participants(undefined as unknown as Array<string>);

// Call broadcast_state
broadcast_state(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call recruit_participants
recruit_participants(undefined as unknown as any, undefined as unknown as Array<string>);
