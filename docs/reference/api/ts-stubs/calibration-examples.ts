// Auto-generated usage examples for calibration
// Source: generate-api-docs.py

import { ConfidenceCalibrator, calibrate, record_feedback } from "./calibration";

// Create a ConfidenceCalibrator instance
const confidencecalibrator = new ConfidenceCalibrator(undefined as unknown as ThegentSettings);
confidencecalibrator.calibrate("example_agent_name", 0);
confidencecalibrator.record_feedback("example_agent_name", 0, false);

// Call calibrate
calibrate(undefined as unknown as any, "example_agent_name", 0);
// Call record_feedback
record_feedback(undefined as unknown as any, "example_agent_name", 0, false);
