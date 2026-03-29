// Auto-generated usage examples for aggregator
// Source: generate-api-docs.py

import { CostAggregator, CostEstimator, daily_total, estimate, get_all_categories_mtd, get_category_mtd_total, get_mtd_total } from "./aggregator";

// Create a CostAggregator instance
const costaggregator = new CostAggregator();
costaggregator.daily_total("example_owner");
costaggregator.get_all_categories_mtd();
costaggregator.get_category_mtd_total("example_category");
costaggregator.get_mtd_total();

// Create a CostEstimator instance
const costestimator = new CostEstimator();
costestimator.estimate(undefined as unknown as any, 0, 0);

// Call daily_total
daily_total(undefined as unknown as any, "example_owner");
// Call estimate
estimate(undefined as unknown as any, undefined as unknown as any, 0, 0);
// Call get_all_categories_mtd
get_all_categories_mtd(undefined as unknown as any);
// Call get_category_mtd_total
get_category_mtd_total(undefined as unknown as any, "example_category");
// Call get_mtd_total
get_mtd_total(undefined as unknown as any);
