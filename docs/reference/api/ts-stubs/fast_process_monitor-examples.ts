// Auto-generated usage examples for fast_process_monitor
// Source: generate-api-docs.py

import { FastProcessMonitor, ProcessInfo, find_by_command, find_processes, get_fast_monitor, get_process, get_process_count, get_process_info_detailed, iter_processes, matches } from "./fast_process_monitor";

// Create a FastProcessMonitor instance
const fastprocessmonitor = new FastProcessMonitor();
fastprocessmonitor.find_by_command(undefined as unknown as Array<string>);
fastprocessmonitor.find_processes(undefined as unknown as Callable<(Any, bool)>);
fastprocessmonitor.get_process(0);
fastprocessmonitor.get_process_count();
fastprocessmonitor.get_process_info_detailed(0);
fastprocessmonitor.iter_processes(undefined as unknown as any, false);

// Create a ProcessInfo instance
const processinfo = new ProcessInfo();

// Call find_by_command
find_by_command(undefined as unknown as any, undefined as unknown as Array<string>);
// Call find_processes
find_processes(undefined as unknown as any, undefined as unknown as Callable<(Any, bool)>);
// Call get_fast_monitor
get_fast_monitor();
// Call get_process
get_process(undefined as unknown as any, 0);
// Call get_process_count
get_process_count(undefined as unknown as any);
// Call get_process_info_detailed
get_process_info_detailed(undefined as unknown as any, 0);
// Call iter_processes
iter_processes(undefined as unknown as any, undefined as unknown as any, false);
// Call matches
matches(undefined as unknown as ProcessInfo);
