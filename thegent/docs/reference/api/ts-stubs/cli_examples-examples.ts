// Auto-generated usage examples for cli_examples
// Source: generate-api-docs.py

import { CLIExamplesGenerator, generate_examples, get_all_commands, render_markdown } from "./cli_examples";

// Create a CLIExamplesGenerator instance
const cliexamplesgenerator = new CLIExamplesGenerator("example_command");
cliexamplesgenerator.generate_examples("example_command");
cliexamplesgenerator.get_all_commands();
cliexamplesgenerator.render_markdown(undefined as unknown as Array<Record<(str, Any)>>);

// Call generate_examples
generate_examples(undefined as unknown as any, "example_command");
// Call get_all_commands
get_all_commands(undefined as unknown as any);
// Call render_markdown
render_markdown(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
