// Auto-generated usage examples for manager
// Source: generate-api-docs.py

import { LayoutManager, LayoutState, PaneConfig, SplitConfig, create_default_layout, create_full_output_layout, create_horizontal_split, create_layout, create_main_sidebar, create_terminal_layout, create_three_column, create_vertical_split, delete_layout, duplicate_layout, get_current, get_layout, list_layouts, rename_layout, switch_layout } from "./manager";

// Create a LayoutManager instance
const layoutmanager = new LayoutManager(undefined as unknown as any);
layoutmanager.create_layout("example_name", undefined as unknown as any);
layoutmanager.delete_layout("example_name");
layoutmanager.duplicate_layout("example_source_name", "example_new_name");
layoutmanager.get_current();
layoutmanager.get_layout("example_name");
layoutmanager.list_layouts();
layoutmanager.rename_layout("example_old_name", "example_new_name");
layoutmanager.switch_layout("example_name");

// Create a LayoutState instance
const layoutstate = new LayoutState();

// Create a PaneConfig instance
const paneconfig = new PaneConfig();

// Create a SplitConfig instance
const splitconfig = new SplitConfig();

// Call create_default_layout
create_default_layout();
// Call create_full_output_layout
create_full_output_layout();
// Call create_horizontal_split
create_horizontal_split(undefined as unknown as PaneConfig, undefined as unknown as PaneConfig, 0, 0);
// Call create_layout
create_layout(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call create_main_sidebar
create_main_sidebar(undefined as unknown as PaneConfig, undefined as unknown as PaneConfig, 0);
// Call create_terminal_layout
create_terminal_layout();
// Call create_three_column
create_three_column(undefined as unknown as PaneConfig, undefined as unknown as PaneConfig, undefined as unknown as PaneConfig, undefined as unknown as any);
// Call create_vertical_split
create_vertical_split(undefined as unknown as PaneConfig, undefined as unknown as PaneConfig, 0, 0);
// Call delete_layout
delete_layout(undefined as unknown as any, "example_name");
// Call duplicate_layout
duplicate_layout(undefined as unknown as any, "example_source_name", "example_new_name");
// Call get_current
get_current(undefined as unknown as any);
// Call get_layout
get_layout(undefined as unknown as any, "example_name");
// Call list_layouts
list_layouts(undefined as unknown as any);
// Call rename_layout
rename_layout(undefined as unknown as any, "example_old_name", "example_new_name");
// Call switch_layout
switch_layout(undefined as unknown as any, "example_name");
