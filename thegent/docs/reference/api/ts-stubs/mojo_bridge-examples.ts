// Auto-generated usage examples for mojo_bridge
// Source: generate-api-docs.py

import { MojoBridge, MojoModule, MojoNotAvailableError, MojoTask, get_bridge, install_instructions, is_available } from "./mojo_bridge";

// Create a MojoBridge instance
const mojobridge = new MojoBridge(undefined as unknown as any, undefined as unknown as any);
mojobridge.install_instructions();
mojobridge.is_available();

// Create a MojoModule instance
const mojomodule = new MojoModule();

// Create a MojoNotAvailableError instance
const mojonotavailableerror = new MojoNotAvailableError();

// Create a MojoTask instance
const mojotask = new MojoTask();

// Call get_bridge
get_bridge();
// Call install_instructions
install_instructions(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
