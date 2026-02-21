// Auto-generated usage examples for billing
// Source: generate-api-docs.py

import { TeamBillingManager, check_quota, get_billing_report, record_usage } from "./billing";

// Create a TeamBillingManager instance
const teambillingmanager = new TeamBillingManager("example_session_dir");
teambillingmanager.check_quota("example_team_id", "example_resource", 0);
teambillingmanager.get_billing_report("example_team_id");
teambillingmanager.record_usage("example_team_id", "example_resource", 0);

// Call check_quota
check_quota(undefined as unknown as any, "example_team_id", "example_resource", 0);
// Call get_billing_report
get_billing_report(undefined as unknown as any, "example_team_id");
// Call record_usage
record_usage(undefined as unknown as any, "example_team_id", "example_resource", 0);
