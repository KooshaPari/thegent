// Auto-generated usage examples for terminal_capture
// Source: generate-api-docs.py

import { CaptureResult, TerminalCapture, capture_by_pid, capture_last_n_lines } from "./terminal_capture";

// Create a CaptureResult instance
const captureresult = new CaptureResult();

// Create a TerminalCapture instance
const terminalcapture = new TerminalCapture();
terminalcapture.capture_by_pid(0, 0);
terminalcapture.capture_last_n_lines(0, undefined as unknown as any);

// Call capture_by_pid
capture_by_pid(undefined as unknown as any, 0, 0);
// Call capture_last_n_lines
capture_last_n_lines(undefined as unknown as any, 0, undefined as unknown as any);
