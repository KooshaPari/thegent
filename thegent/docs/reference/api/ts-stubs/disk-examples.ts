// Auto-generated usage examples for disk
// Source: generate-api-docs.py

import { DiskIoStats, DiskMonitor, DiskQueueSample, get_disk_usage, get_io_stats, list_devices, sample_queue_depth } from "./disk";

// Create a DiskIoStats instance
const diskiostats = new DiskIoStats();

// Create a DiskMonitor instance
const diskmonitor = new DiskMonitor();
diskmonitor.get_disk_usage("example_path");
diskmonitor.get_io_stats(undefined as unknown as any);
diskmonitor.list_devices();
diskmonitor.sample_queue_depth(0);

// Create a DiskQueueSample instance
const diskqueuesample = new DiskQueueSample();

// Call get_disk_usage
get_disk_usage(undefined as unknown as any, "example_path");
// Call get_io_stats
get_io_stats(undefined as unknown as any, undefined as unknown as any);
// Call list_devices
list_devices(undefined as unknown as any);
// Call sample_queue_depth
sample_queue_depth(undefined as unknown as any, 0);
