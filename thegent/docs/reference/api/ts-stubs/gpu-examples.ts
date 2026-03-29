// Auto-generated usage examples for gpu
// Source: generate-api-docs.py

import { GpuInfo, GpuMonitor, GpuMonitorError, get_gpus, get_total_utilization, is_available } from "./gpu";

// Create a GpuInfo instance
const gpuinfo = new GpuInfo();

// Create a GpuMonitor instance
const gpumonitor = new GpuMonitor();
gpumonitor.get_gpus();
gpumonitor.get_total_utilization();
gpumonitor.is_available();

// Create a GpuMonitorError instance
const gpumonitorerror = new GpuMonitorError();

// Call get_gpus
get_gpus(undefined as unknown as any);
// Call get_total_utilization
get_total_utilization(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
