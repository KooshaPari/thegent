// Auto-generated usage examples for geo_guard
// Source: generate-api-docs.py

import { DataLocationCheck, GeoGuard, SovereigntyRule, add_rule, validate_location } from "./geo_guard";

// Create a DataLocationCheck instance
const datalocationcheck = new DataLocationCheck();

// Create a GeoGuard instance
const geoguard = new GeoGuard();
geoguard.add_rule(undefined as unknown as SovereigntyRule);
geoguard.validate_location("example_data_id", "example_category", "example_region");

// Create a SovereigntyRule instance
const sovereigntyrule = new SovereigntyRule();

// Call add_rule
add_rule(undefined as unknown as any, undefined as unknown as SovereigntyRule);
// Call validate_location
validate_location(undefined as unknown as any, "example_data_id", "example_category", "example_region");
