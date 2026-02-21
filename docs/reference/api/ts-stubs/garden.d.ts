// Auto-generated TypeScript declarations for garden
// Source: generate-api-docs.py

export declare class GardenCluster {
}

export declare class MemoryGarden {
  constructor(garden_path: string);
  add_to_cluster(cluster_id: string, seed: Seed): void;
  find_best_cluster(seed: Seed): void;
  save(): void;
  synthesize(): void;
}

export declare function add_to_cluster(cluster_id: string, seed: Seed): void;
export declare function find_best_cluster(seed: Seed): void;
export declare function save(): void;
export declare function synthesize(): void;
