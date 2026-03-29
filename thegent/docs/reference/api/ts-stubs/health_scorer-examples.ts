// Auto-generated usage examples for health_scorer
// Source: generate-api-docs.py

import { DimensionScore, HealthReport, HealthScorer, calculate_overall, dimension_status, generate_report, normalize_score, score_dimension } from "./health_scorer";

// Create a DimensionScore instance
const dimensionscore = new DimensionScore();

// Create a HealthReport instance
const healthreport = new HealthReport();

// Create a HealthScorer instance
const healthscorer = new HealthScorer(undefined as unknown as any);
healthscorer.calculate_overall(undefined as unknown as Array<DimensionScore>);
healthscorer.dimension_status(0);
healthscorer.generate_report(undefined as unknown as Record<(str, float)>);
healthscorer.normalize_score(0, 0, "example_direction");
healthscorer.score_dimension("example_dimension_key", 0);

// Call calculate_overall
calculate_overall(undefined as unknown as any, undefined as unknown as Array<DimensionScore>);
// Call dimension_status
dimension_status(undefined as unknown as any, 0);
// Call generate_report
generate_report(undefined as unknown as any, undefined as unknown as Record<(str, float)>);
// Call normalize_score
normalize_score(undefined as unknown as any, 0, 0, "example_direction");
// Call score_dimension
score_dimension(undefined as unknown as any, "example_dimension_key", 0);
