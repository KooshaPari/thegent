// Auto-generated usage examples for demo_gif_generator
// Source: generate-api-docs.py

import { DemoGIFGenerator, generate_from_commands, generate_from_script } from "./demo_gif_generator";

// Create a DemoGIFGenerator instance
const demogifgenerator = new DemoGIFGenerator(undefined as unknown as any);
demogifgenerator.generate_from_commands(undefined as unknown as Array<string>, "example_output_path");
demogifgenerator.generate_from_script("example_script_path", "example_output_path");

// Call generate_from_commands
generate_from_commands(undefined as unknown as any, undefined as unknown as Array<string>, "example_output_path");
// Call generate_from_script
generate_from_script(undefined as unknown as any, "example_script_path", "example_output_path");
