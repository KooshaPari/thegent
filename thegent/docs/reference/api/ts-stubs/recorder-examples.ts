// Auto-generated usage examples for recorder
// Source: generate-api-docs.py

import { RecorderConfig, RedactionConfig, TraceCleanup, TraceRecorder, TruncationConfig, delete_trace, get_trace_file_size } from "./recorder";

// Create a RecorderConfig instance
const recorderconfig = new RecorderConfig();

// Create a RedactionConfig instance
const redactionconfig = new RedactionConfig();

// Create a TraceCleanup instance
const tracecleanup = new TraceCleanup("example_trace_dir", 0);

// Create a TraceRecorder instance
const tracerecorder = new TraceRecorder("example_session_id", undefined as unknown as any);
tracerecorder.delete_trace();
tracerecorder.get_trace_file_size();

// Create a TruncationConfig instance
const truncationconfig = new TruncationConfig();

// Call delete_trace
delete_trace(undefined as unknown as any);
// Call get_trace_file_size
get_trace_file_size(undefined as unknown as any);
