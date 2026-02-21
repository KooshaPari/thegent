// Auto-generated usage examples for os_user_manager
// Source: generate-api-docs.py

import { OSUser, OSUserManager, create_user, delete_user } from "./os_user_manager";

// Create a OSUser instance
const osuser = new OSUser();

// Create a OSUserManager instance
const osusermanager = new OSUserManager("example_prefix");
osusermanager.create_user("example_name", undefined as unknown as any);
osusermanager.delete_user("example_username", false);

// Call create_user
create_user(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call delete_user
delete_user(undefined as unknown as any, "example_username", false);
