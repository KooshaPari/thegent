// Auto-generated TypeScript declarations for demo_gif_generator
// Source: generate-api-docs.py

export declare class DemoGIFGenerator {
  constructor(vhs_path: any);
  generate_from_commands(commands: Array<string>, output_path: string): void;
  generate_from_script(script_path: string, output_path: string): void;
}

export declare function generate_from_commands(commands: Array<string>, output_path: string): void;
export declare function generate_from_script(script_path: string, output_path: string): void;
