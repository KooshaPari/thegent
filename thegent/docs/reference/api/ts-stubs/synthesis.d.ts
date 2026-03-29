// Auto-generated TypeScript declarations for synthesis
// Source: generate-api-docs.py

export declare class ProgramSynthesizer {
  constructor(run_id: string);
  synthesize(prompt: string, formal_spec: any): void;
}

export declare class SynthesisResult extends BaseModel {
}

export declare function synthesize(prompt: string, formal_spec: any): void;
