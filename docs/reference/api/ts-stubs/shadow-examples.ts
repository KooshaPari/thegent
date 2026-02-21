// Auto-generated usage examples for shadow
// Source: generate-api-docs.py

import { ShadowWorkspace, create, destroy, get_env, merge_back, run } from "./shadow";

// Create a ShadowWorkspace instance
const shadowworkspace = new ShadowWorkspace("example_project_root", "example_shadow_id");
shadowworkspace.create(undefined as unknown as any);
shadowworkspace.destroy();
shadowworkspace.get_env();
shadowworkspace.merge_back();
shadowworkspace.run(undefined as unknown as Array<string>);

// Call create
create(undefined as unknown as any, undefined as unknown as any);
// Call destroy
destroy(undefined as unknown as any);
// Call get_env
get_env(undefined as unknown as any);
// Call merge_back
merge_back(undefined as unknown as any);
// Call run
run(undefined as unknown as any, undefined as unknown as Array<string>);
