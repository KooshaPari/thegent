// Auto-generated TypeScript declarations for otel_instrumentation
// Source: generate-api-docs.py

export declare function instrument_genai_call(agent_name: string, model: string, run_id: any, chunk_id: any, system: any): void;
export declare function record_usage(span: trace.Span, input_tokens: number, output_tokens: number): void;
