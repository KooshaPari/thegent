// Auto-generated usage examples for health_score
// Source: generate-api-docs.py

import { DimensionScore, HealthBand, HealthScore, HealthScoreComputer, compute, compute_with_trend, get_band } from "./health_score";

// Create a DimensionScore instance
const dimensionscore = new DimensionScore();

// Create a HealthBand instance
const healthband = new HealthBand();

// Create a HealthScore instance
const healthscore = new HealthScore();

// Create a HealthScoreComputer instance
const healthscorecomputer = new HealthScoreComputer("example_health_targets_path");
healthscorecomputer.compute(undefined as unknown as Record<(str, float)>);
healthscorecomputer.compute_with_trend(undefined as unknown as Record<(str, float)>, undefined as unknown as any);

// Call compute
compute(undefined as unknown as any, undefined as unknown as Record<(str, float)>);
// Call compute_with_trend
compute_with_trend(undefined as unknown as any, undefined as unknown as Record<(str, float)>, undefined as unknown as any);
// Call get_band
get_band(0);
