// Auto-generated TypeScript declarations for analyzer
// Source: generate-api-docs.py

export declare class DocumentAnalysis {
  to_dict(): void;
}

export declare class DocumentAnalyzer {
  constructor();
  analyze(filepath: string): void;
}

export declare class DocumentCategory extends Enum {
}

export declare function analyze(filepath: string): void;
export declare function to_dict(): void;
