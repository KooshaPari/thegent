// Auto-generated usage examples for storage
// Source: generate-api-docs.py

import { PromptQueue, append, claim, done, edit, extend_lease, get_pending_count, list_all, list_pending, release } from "./storage";

// Create a PromptQueue instance
const promptqueue = new PromptQueue("example_session_dir");
promptqueue.append("example_prompt", "example_project", undefined as unknown as any);
promptqueue.claim("example_claimer_id", 0, undefined as unknown as any);
promptqueue.done(0);
promptqueue.edit(0, "example_prompt");
promptqueue.extend_lease(0, 0);
promptqueue.get_pending_count();
promptqueue.list_all(false, false, undefined as unknown as any);
promptqueue.list_pending();
promptqueue.release(0);

// Call append
append(undefined as unknown as any, "example_prompt", "example_project", undefined as unknown as any);
// Call claim
claim(undefined as unknown as any, "example_claimer_id", 0, undefined as unknown as any);
// Call done
done(undefined as unknown as any, 0);
// Call edit
edit(undefined as unknown as any, 0, "example_prompt");
// Call extend_lease
extend_lease(undefined as unknown as any, 0, 0);
// Call get_pending_count
get_pending_count(undefined as unknown as any);
// Call list_all
list_all(undefined as unknown as any, false, false, undefined as unknown as any);
// Call list_pending
list_pending(undefined as unknown as any);
// Call release
release(undefined as unknown as any, 0);
