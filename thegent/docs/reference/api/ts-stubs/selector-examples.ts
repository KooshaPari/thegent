// Auto-generated usage examples for selector
// Source: generate-api-docs.py

import { ObjectiveSelector, ObjectiveWeights, get_objective_profile, score_model, select, select_best_model, validate } from "./selector";

// Create a ObjectiveSelector instance
const objectiveselector = new ObjectiveSelector(undefined as unknown as any);
objectiveselector.select(undefined as unknown as Array<Record<(str, Any)>>, undefined as unknown as any);
objectiveselector.select_best_model(undefined as unknown as Array<string>);

// Create a ObjectiveWeights instance
const objectiveweights = new ObjectiveWeights();
objectiveweights.validate();

// Call get_objective_profile
get_objective_profile("example_profile_name");
// Call score_model
score_model(undefined as unknown as any);
// Call select
select(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>, undefined as unknown as any);
// Call select_best_model
select_best_model(undefined as unknown as any, undefined as unknown as Array<string>);
// Call validate
validate(undefined as unknown as any);
