// Auto-generated usage examples for rbac
// Source: generate-api-docs.py

import { Permission, RBACManager, Role, check_access, has_permission } from "./rbac";

// Create a Permission instance
const permission = new Permission();

// Create a RBACManager instance
const rbacmanager = new RBACManager();
rbacmanager.check_access(undefined as unknown as Role, "example_operation", "example_lane");
rbacmanager.has_permission(undefined as unknown as Role, undefined as unknown as Permission);

// Create a Role instance
const role = new Role();

// Call check_access
check_access(undefined as unknown as any, undefined as unknown as Role, "example_operation", "example_lane");
// Call has_permission
has_permission(undefined as unknown as any, undefined as unknown as Role, undefined as unknown as Permission);
