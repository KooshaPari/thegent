// Auto-generated usage examples for frecency
// Source: generate-api-docs.py

import { FrecencyCache, FrecencyEntry, FrecencyModelSelector, access, age_seconds, cache, clear, evict_lowest, get_entry, half_life, maxsize, preferred_model, recalculate_score, record_use, score, top_models, top_n } from "./frecency";

// Create a FrecencyCache instance
const frecencycache = new FrecencyCache(0, 0, undefined as unknown as any);
frecencycache.access("example_key");
frecencycache.clear();
frecencycache.evict_lowest(0);
frecencycache.get_entry("example_key");
frecencycache.half_life();
frecencycache.maxsize();
frecencycache.score("example_key");
frecencycache.top_n(0);

// Create a FrecencyEntry instance
const frecencyentry = new FrecencyEntry();
frecencyentry.age_seconds(undefined as unknown as any);
frecencyentry.recalculate_score(0, undefined as unknown as any);

// Create a FrecencyModelSelector instance
const frecencymodelselector = new FrecencyModelSelector(0, 0, undefined as unknown as any);
frecencymodelselector.cache();
frecencymodelselector.preferred_model(undefined as unknown as Array<string>);
frecencymodelselector.record_use("example_model_id");
frecencymodelselector.score("example_model_id");
frecencymodelselector.top_models(0);

// Call access
access(undefined as unknown as any, "example_key");
// Call age_seconds
age_seconds(undefined as unknown as any, undefined as unknown as any);
// Call cache
cache(undefined as unknown as any);
// Call clear
clear(undefined as unknown as any);
// Call evict_lowest
evict_lowest(undefined as unknown as any, 0);
// Call get_entry
get_entry(undefined as unknown as any, "example_key");
// Call half_life
half_life(undefined as unknown as any);
// Call maxsize
maxsize(undefined as unknown as any);
// Call preferred_model
preferred_model(undefined as unknown as any, undefined as unknown as Array<string>);
// Call recalculate_score
recalculate_score(undefined as unknown as any, 0, undefined as unknown as any);
// Call record_use
record_use(undefined as unknown as any, "example_model_id");
// Call score
score(undefined as unknown as any, "example_model_id");
// Call top_models
top_models(undefined as unknown as any, 0);
// Call top_n
top_n(undefined as unknown as any, 0);
