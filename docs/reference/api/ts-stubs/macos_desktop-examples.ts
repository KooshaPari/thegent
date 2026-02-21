// Auto-generated usage examples for macos_desktop
// Source: generate-api-docs.py

import { AutomationError, AutomationResult, MacOSDesktopAutomation, click_menu_item, get_frontmost_app, is_available, open_application, run_applescript, run_jxa } from "./macos_desktop";

// Create a AutomationError instance
const automationerror = new AutomationError();

// Create a AutomationResult instance
const automationresult = new AutomationResult();

// Create a MacOSDesktopAutomation instance
const macosdesktopautomation = new MacOSDesktopAutomation();
macosdesktopautomation.click_menu_item("example_app", "example_menu", "example_item");
macosdesktopautomation.get_frontmost_app();
macosdesktopautomation.is_available();
macosdesktopautomation.open_application("example_name");
macosdesktopautomation.run_applescript("example_script", 0);
macosdesktopautomation.run_jxa("example_script", 0);

// Call click_menu_item
click_menu_item(undefined as unknown as any, "example_app", "example_menu", "example_item");
// Call get_frontmost_app
get_frontmost_app(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call open_application
open_application(undefined as unknown as any, "example_name");
// Call run_applescript
run_applescript(undefined as unknown as any, "example_script", 0);
// Call run_jxa
run_jxa(undefined as unknown as any, "example_script", 0);
