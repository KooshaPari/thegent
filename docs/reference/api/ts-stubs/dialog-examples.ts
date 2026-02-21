// Auto-generated usage examples for dialog
// Source: generate-api-docs.py

import { ConfirmDialog, Dialog, DialogManager, DialogResult, DialogStyle, InputDialog, MessageDialog, Overlay, Toast, close_all, compose, dismiss, get_value, on_click, on_key, on_mount, on_result, show_confirm, show_dialog, show_input, show_message, show_toast } from "./dialog";

// Create a ConfirmDialog instance
const confirmdialog = new ConfirmDialog("example_message", "example_title", "example_yes_label", "example_no_label");

// Create a Dialog instance
const dialog = new Dialog("example_title");
dialog.compose();
dialog.on_click(undefined as unknown as Click);
dialog.on_key(undefined as unknown as Key);
dialog.on_mount();
dialog.on_result(undefined as unknown as Callable<(Any, None)>);

// Create a DialogManager instance
const dialogmanager = new DialogManager();
dialogmanager.close_all();
dialogmanager.show_confirm("example_message", "example_title", undefined as unknown as any);
dialogmanager.show_dialog(undefined as unknown as Dialog);
dialogmanager.show_input("example_prompt", "example_title", "example_default", false, undefined as unknown as any);
dialogmanager.show_message("example_message", "example_title", undefined as unknown as DialogStyle);
dialogmanager.show_toast("example_message", 0, undefined as unknown as DialogStyle);

// Create a DialogResult instance
const dialogresult = new DialogResult();

// Create a DialogStyle instance
const dialogstyle = new DialogStyle();

// Create a InputDialog instance
const inputdialog = new InputDialog("example_prompt", "example_title", "example_default", false, "example_placeholder");
inputdialog.get_value();

// Create a MessageDialog instance
const messagedialog = new MessageDialog("example_message", "example_title");

// Create a Overlay instance
const overlay = new Overlay();

// Create a Toast instance
const toast = new Toast("example_message", 0, undefined as unknown as DialogStyle);
toast.compose();
toast.dismiss();
toast.on_mount();

// Call close_all
close_all(undefined as unknown as any);
// Call compose
compose(undefined as unknown as any);
// Call dismiss
dismiss(undefined as unknown as any);
// Call get_value
get_value(undefined as unknown as any);
// Call on_click
on_click(undefined as unknown as any, undefined as unknown as Click);
// Call on_key
on_key(undefined as unknown as any, undefined as unknown as Key);
// Call on_mount
on_mount(undefined as unknown as any);
// Call on_result
on_result(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>);
// Call show_confirm
show_confirm(undefined as unknown as any, "example_message", "example_title", undefined as unknown as any);
// Call show_dialog
show_dialog(undefined as unknown as any, undefined as unknown as Dialog);
// Call show_input
show_input(undefined as unknown as any, "example_prompt", "example_title", "example_default", false, undefined as unknown as any);
// Call show_message
show_message(undefined as unknown as any, "example_message", "example_title", undefined as unknown as DialogStyle);
// Call show_toast
show_toast(undefined as unknown as any, "example_message", 0, undefined as unknown as DialogStyle);
