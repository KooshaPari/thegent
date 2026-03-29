// Auto-generated usage examples for policy
// Source: generate-api-docs.py

import { LearningSession, PolicyManager, get_policy, is_valid, start, update } from "./policy";

// Create a LearningSession instance
const learningsession = new LearningSession(undefined as unknown as PolicyManager);
learningsession.is_valid();
learningsession.start();

// Create a PolicyManager instance
const policymanager = new PolicyManager(undefined as unknown as any);
policymanager.get_policy("example_key");
policymanager.update(undefined as unknown as Record<(str, Any)>);

// Call get_policy
get_policy(undefined as unknown as any, "example_key");
// Call is_valid
is_valid(undefined as unknown as any);
// Call start
start(undefined as unknown as any);
// Call update
update(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
