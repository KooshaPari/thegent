// Auto-generated usage examples for compositor_manager
// Source: generate-api-docs.py

import { CompositorManager, CompositorSlot, Layout, add_compositor, focus, get_compositor, get_focused, layout, remove_compositor, render_all, slot_ids, switch_layout } from "./compositor_manager";

// Create a CompositorManager instance
const compositormanager = new CompositorManager(undefined as unknown as Layout);
compositormanager.add_compositor(undefined as unknown as Compositor, "example_slot_id", 0);
compositormanager.focus("example_slot_id");
compositormanager.get_compositor("example_slot_id");
compositormanager.get_focused();
compositormanager.layout();
compositormanager.remove_compositor("example_slot_id");
compositormanager.render_all(0);
compositormanager.slot_ids();
compositormanager.switch_layout(undefined as unknown as Layout);

// Create a CompositorSlot instance
const compositorslot = new CompositorSlot();

// Create a Layout instance
const layout = new Layout();

// Call add_compositor
add_compositor(undefined as unknown as any, undefined as unknown as Compositor, "example_slot_id", 0);
// Call focus
focus(undefined as unknown as any, "example_slot_id");
// Call get_compositor
get_compositor(undefined as unknown as any, "example_slot_id");
// Call get_focused
get_focused(undefined as unknown as any);
// Call layout
layout(undefined as unknown as any);
// Call remove_compositor
remove_compositor(undefined as unknown as any, "example_slot_id");
// Call render_all
render_all(undefined as unknown as any, 0);
// Call slot_ids
slot_ids(undefined as unknown as any);
// Call switch_layout
switch_layout(undefined as unknown as any, undefined as unknown as Layout);
