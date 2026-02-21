// Auto-generated usage examples for garden
// Source: generate-api-docs.py

import { GardenCluster, MemoryGarden, add_to_cluster, find_best_cluster, save, synthesize } from "./garden";

// Create a GardenCluster instance
const gardencluster = new GardenCluster();

// Create a MemoryGarden instance
const memorygarden = new MemoryGarden("example_garden_path");
memorygarden.add_to_cluster("example_cluster_id", undefined as unknown as Seed);
memorygarden.find_best_cluster(undefined as unknown as Seed);
memorygarden.save();
memorygarden.synthesize();

// Call add_to_cluster
add_to_cluster(undefined as unknown as any, "example_cluster_id", undefined as unknown as Seed);
// Call find_best_cluster
find_best_cluster(undefined as unknown as any, undefined as unknown as Seed);
// Call save
save(undefined as unknown as any);
// Call synthesize
synthesize(undefined as unknown as any);
