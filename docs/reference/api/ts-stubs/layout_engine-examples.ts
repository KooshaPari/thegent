// Auto-generated usage examples for layout_engine
// Source: generate-api-docs.py

import { Direction, LayoutConstraints, LayoutEngine, LayoutNode, Margin, Padding, Size, SizeUnit, add_child, calculate_layout, create_grid, create_horizontal_stack, create_vertical_stack, generate_css, generate_layout_css, get_css_for_child, get_widget, register_widget, to_dict, to_textual_css } from "./layout_engine";

// Create a Direction instance
const direction = new Direction();

// Create a LayoutConstraints instance
const layoutconstraints = new LayoutConstraints();

// Create a LayoutEngine instance
const layoutengine = new LayoutEngine();
layoutengine.calculate_layout(0, 0);
layoutengine.create_grid(0, 0, undefined as unknown as Array<string>);
layoutengine.create_horizontal_stack(undefined as unknown as Array<string>, undefined as unknown as any);
layoutengine.create_vertical_stack(undefined as unknown as Array<string>, undefined as unknown as any);
layoutengine.generate_layout_css();
layoutengine.get_widget("example_widget_id");
layoutengine.register_widget("example_widget_id", undefined as unknown as object);

// Create a LayoutNode instance
const layoutnode = new LayoutNode(undefined as unknown as Direction, undefined as unknown as any);
layoutnode.add_child(undefined as unknown as any, undefined as unknown as any);
layoutnode.generate_css(0);
layoutnode.get_css_for_child(0);
layoutnode.to_dict();

// Create a Margin instance
const margin = new Margin();
margin.to_textual_css();

// Create a Padding instance
const padding = new Padding();
padding.to_textual_css();

// Create a Size instance
const size = new Size(0, undefined as unknown as any);
size.to_textual_css();

// Create a SizeUnit instance
const sizeunit = new SizeUnit();

// Call add_child
add_child(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call calculate_layout
calculate_layout(undefined as unknown as any, 0, 0);
// Call create_grid
create_grid(undefined as unknown as any, 0, 0, undefined as unknown as Array<string>);
// Call create_horizontal_stack
create_horizontal_stack(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as any);
// Call create_vertical_stack
create_vertical_stack(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as any);
// Call generate_css
generate_css(undefined as unknown as any, 0);
// Call generate_layout_css
generate_layout_css(undefined as unknown as any);
// Call get_css_for_child
get_css_for_child(undefined as unknown as any, 0);
// Call get_widget
get_widget(undefined as unknown as any, "example_widget_id");
// Call register_widget
register_widget(undefined as unknown as any, "example_widget_id", undefined as unknown as object);
// Call to_dict
to_dict(undefined as unknown as any);
// Call to_textual_css
to_textual_css(undefined as unknown as any);
