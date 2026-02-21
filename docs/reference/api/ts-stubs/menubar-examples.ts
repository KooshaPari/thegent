// Auto-generated usage examples for menubar
// Source: generate-api-docs.py

import { MenuDropdown, MenubarWidget, action_toggle_menu, compose, on_click, on_mount } from "./menubar";

// Create a MenuDropdown instance
const menudropdown = new MenuDropdown(undefined as unknown as Array<[(str, Any)]>);
menudropdown.compose();

// Create a MenubarWidget instance
const menubarwidget = new MenubarWidget();
menubarwidget.action_toggle_menu("example_menu_name");
menubarwidget.compose();
menubarwidget.on_click(undefined as unknown as Click);
menubarwidget.on_mount();

// Call action_toggle_menu
action_toggle_menu(undefined as unknown as any, "example_menu_name");
// Call compose
compose(undefined as unknown as any);
// Call on_click
on_click(undefined as unknown as any, undefined as unknown as Click);
// Call on_mount
on_mount(undefined as unknown as any);
