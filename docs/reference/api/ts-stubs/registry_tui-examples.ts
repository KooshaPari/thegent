// Auto-generated usage examples for registry_tui
// Source: generate-api-docs.py

import { RegistryTUI, SessionDetails, action_refresh, action_toggle_all, compose, on_mount, on_session_selected, update_details } from "./registry_tui";

// Create a RegistryTUI instance
const registrytui = new RegistryTUI();
registrytui.action_refresh();
registrytui.action_toggle_all();
registrytui.compose();
registrytui.on_mount();
registrytui.on_session_selected(undefined as unknown as DataTable.RowSelected);

// Create a SessionDetails instance
const sessiondetails = new SessionDetails();
sessiondetails.update_details(undefined as unknown as Record<(str, Any)>);

// Call action_refresh
action_refresh(undefined as unknown as any);
// Call action_toggle_all
action_toggle_all(undefined as unknown as any);
// Call compose
compose(undefined as unknown as any);
// Call on_mount
on_mount(undefined as unknown as any);
// Call on_session_selected
on_session_selected(undefined as unknown as any, undefined as unknown as DataTable.RowSelected);
// Call update_details
update_details(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
