// Auto-generated usage examples for network
// Source: generate-api-docs.py

import { BandwidthSample, NetworkMonitor, NetworkStats, get_stats, get_total_bandwidth, list_interfaces, sample_bandwidth } from "./network";

// Create a BandwidthSample instance
const bandwidthsample = new BandwidthSample();

// Create a NetworkMonitor instance
const networkmonitor = new NetworkMonitor();
networkmonitor.get_stats(undefined as unknown as any);
networkmonitor.get_total_bandwidth();
networkmonitor.list_interfaces();
networkmonitor.sample_bandwidth(0);

// Create a NetworkStats instance
const networkstats = new NetworkStats();

// Call get_stats
get_stats(undefined as unknown as any, undefined as unknown as any);
// Call get_total_bandwidth
get_total_bandwidth(undefined as unknown as any);
// Call list_interfaces
list_interfaces(undefined as unknown as any);
// Call sample_bandwidth
sample_bandwidth(undefined as unknown as any, 0);
