// Auto-generated usage examples for compositor
// Source: generate-api-docs.py

import { CacheStats, Compositor, CompositorProfiler, Panel, RenderProfile, add_panel, cache_stats, clear, errored_panels, get_average, get_panel, get_slowest, has_error, invalidate, panel_names, record, record_count, recover, recover_all, recover_panel, remove_panel, render, render_all, render_panel, report } from "./compositor";

// Create a CacheStats instance
const cachestats = new CacheStats();

// Create a Compositor instance
const compositor = new Compositor(0, 0, 0);
compositor.add_panel(undefined as unknown as Panel);
compositor.cache_stats();
compositor.errored_panels();
compositor.get_panel("example_name");
compositor.invalidate(undefined as unknown as any);
compositor.panel_names();
compositor.recover_all();
compositor.recover_panel("example_name");
compositor.remove_panel("example_name");
compositor.render();
compositor.render_all();
compositor.render_panel("example_name");

// Create a CompositorProfiler instance
const compositorprofiler = new CompositorProfiler();
compositorprofiler.clear();
compositorprofiler.get_average(undefined as unknown as any);
compositorprofiler.get_slowest(0);
compositorprofiler.record(undefined as unknown as RenderProfile);
compositorprofiler.record_count();
compositorprofiler.report();

// Create a Panel instance
const panel = new Panel();
panel.has_error();
panel.recover();
panel.render();

// Create a RenderProfile instance
const renderprofile = new RenderProfile();

// Call add_panel
add_panel(undefined as unknown as any, undefined as unknown as Panel);
// Call cache_stats
cache_stats(undefined as unknown as any);
// Call clear
clear(undefined as unknown as any);
// Call errored_panels
errored_panels(undefined as unknown as any);
// Call get_average
get_average(undefined as unknown as any, undefined as unknown as any);
// Call get_panel
get_panel(undefined as unknown as any, "example_name");
// Call get_slowest
get_slowest(undefined as unknown as any, 0);
// Call has_error
has_error(undefined as unknown as any);
// Call invalidate
invalidate(undefined as unknown as any, undefined as unknown as any);
// Call panel_names
panel_names(undefined as unknown as any);
// Call record
record(undefined as unknown as any, undefined as unknown as RenderProfile);
// Call record_count
record_count(undefined as unknown as any);
// Call recover
recover(undefined as unknown as any);
// Call recover_all
recover_all(undefined as unknown as any);
// Call recover_panel
recover_panel(undefined as unknown as any, "example_name");
// Call remove_panel
remove_panel(undefined as unknown as any, "example_name");
// Call render
render(undefined as unknown as any);
// Call render_all
render_all(undefined as unknown as any);
// Call render_panel
render_panel(undefined as unknown as any, "example_name");
// Call report
report(undefined as unknown as any);
