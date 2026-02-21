// Auto-generated TypeScript declarations for seed_detector
// Source: generate-api-docs.py

export declare class Seed {
  to_dict(): void;
}

export declare class SeedConfidence extends Enum {
}

export declare class SeedDetector {
  constructor(use_llm: boolean);
  detect_seeds(text: string, source: SeedSource): void;
  extract_flags(text: string): void;
}

export declare class SeedSource extends Enum {
}

export declare function detect_seeds(text: string, source: SeedSource): void;
export declare function extract_flags(text: string): void;
export declare function to_dict(): void;
