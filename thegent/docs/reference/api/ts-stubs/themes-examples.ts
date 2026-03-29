// Auto-generated usage examples for themes
// Source: generate-api-docs.py

import { ThemeColors, ThemeDefinition, ThemeManager, add_theme, apply_to_app, create_theme, delete_theme, duplicate_theme, export_theme, from_dict, get_builtin_themes, get_current, get_styles, get_theme, import_theme, list_themes, set_theme, to_dict, to_textual_theme } from "./themes";

// Create a ThemeColors instance
const themecolors = new ThemeColors();
themecolors.from_dict(undefined as unknown as Record<(str, str)>);
themecolors.to_dict();

// Create a ThemeDefinition instance
const themedefinition = new ThemeDefinition();
themedefinition.from_dict(undefined as unknown as Record<(str, Any)>);
themedefinition.to_dict();
themedefinition.to_textual_theme();

// Create a ThemeManager instance
const thememanager = new ThemeManager(undefined as unknown as any);
thememanager.add_theme(undefined as unknown as ThemeDefinition);
thememanager.apply_to_app(undefined as unknown as any);
thememanager.create_theme("example_name", undefined as unknown as ThemeColors, false, "example_author", "example_description");
thememanager.delete_theme("example_name");
thememanager.duplicate_theme("example_source", "example_new_name");
thememanager.export_theme("example_name", "example_path");
thememanager.get_current();
thememanager.get_styles();
thememanager.get_theme("example_name");
thememanager.import_theme("example_path");
thememanager.list_themes();
thememanager.set_theme("example_name");

// Call add_theme
add_theme(undefined as unknown as any, undefined as unknown as ThemeDefinition);
// Call apply_to_app
apply_to_app(undefined as unknown as any, undefined as unknown as any);
// Call create_theme
create_theme(undefined as unknown as any, "example_name", undefined as unknown as ThemeColors, false, "example_author", "example_description");
// Call delete_theme
delete_theme(undefined as unknown as any, "example_name");
// Call duplicate_theme
duplicate_theme(undefined as unknown as any, "example_source", "example_new_name");
// Call export_theme
export_theme(undefined as unknown as any, "example_name", "example_path");
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_builtin_themes
get_builtin_themes();
// Call get_current
get_current(undefined as unknown as any);
// Call get_styles
get_styles(undefined as unknown as any);
// Call get_theme
get_theme(undefined as unknown as any, "example_name");
// Call import_theme
import_theme(undefined as unknown as any, "example_path");
// Call list_themes
list_themes(undefined as unknown as any);
// Call set_theme
set_theme(undefined as unknown as any, "example_name");
// Call to_dict
to_dict(undefined as unknown as any);
// Call to_textual_theme
to_textual_theme(undefined as unknown as any);
