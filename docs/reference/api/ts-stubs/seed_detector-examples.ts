// Auto-generated usage examples for seed_detector
// Source: generate-api-docs.py

import { Seed, SeedConfidence, SeedDetector, SeedSource, detect_seeds, extract_flags, to_dict } from "./seed_detector";

// Create a Seed instance
const seed = new Seed();
seed.to_dict();

// Create a SeedConfidence instance
const seedconfidence = new SeedConfidence();

// Create a SeedDetector instance
const seeddetector = new SeedDetector(false);
seeddetector.detect_seeds("example_text", undefined as unknown as SeedSource);
seeddetector.extract_flags("example_text");

// Create a SeedSource instance
const seedsource = new SeedSource();

// Call detect_seeds
detect_seeds(undefined as unknown as any, "example_text", undefined as unknown as SeedSource);
// Call extract_flags
extract_flags("example_text");
// Call to_dict
to_dict(undefined as unknown as any);
