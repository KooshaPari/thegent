// Auto-generated usage examples for symbolic
// Source: generate-api-docs.py

import { RiskPath, SymbolicRiskExplorer, explore, get_highest_risk_path } from "./symbolic";

// Create a RiskPath instance
const riskpath = new RiskPath();

// Create a SymbolicRiskExplorer instance
const symbolicriskexplorer = new SymbolicRiskExplorer(undefined as unknown as Record<(str, Any)>);
symbolicriskexplorer.explore("example_start_node");
symbolicriskexplorer.get_highest_risk_path();

// Call explore
explore(undefined as unknown as any, "example_start_node");
// Call get_highest_risk_path
get_highest_risk_path(undefined as unknown as any);
