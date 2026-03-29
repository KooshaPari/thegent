// Auto-generated TypeScript declarations for autopoiesis
// Source: generate-api-docs.py

export declare class AgentPersonaSpec extends BaseModel {
}

export declare class AutopoiesisManager {
  constructor(run_id: string);
  author_persona(spec: AgentPersonaSpec): void;
  deploy_persona(synthesis: SynthesisResult): void;
}

export declare function author_persona(spec: AgentPersonaSpec): void;
export declare function deploy_persona(synthesis: SynthesisResult): void;
