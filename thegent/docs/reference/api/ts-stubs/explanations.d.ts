// Auto-generated TypeScript declarations for explanations
// Source: generate-api-docs.py

export declare class ExplanationGenerator {
  constructor(settings: ThegentSettings);
  generate_explanation(data: Record<(str, Any)>, tier: ExplanationTier): void;
}

export declare class ExplanationTier extends enum.StrEnum {
}

export declare function generate_explanation(data: Record<(str, Any)>, tier: ExplanationTier): void;
