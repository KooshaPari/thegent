// Auto-generated usage examples for shell_config
// Source: generate-api-docs.py

import { ShellConfigAuditor, ShellConfigFile, audit, check_sourcing_order, find_duplicate_aliases, find_duplicates, generate_consolidated, parse, sourcing_graph } from "./shell_config";

// Create a ShellConfigAuditor instance
const shellconfigauditor = new ShellConfigAuditor();
shellconfigauditor.audit(undefined as unknown as Array<string>);
shellconfigauditor.check_sourcing_order(undefined as unknown as Array<ShellConfigFile>);
shellconfigauditor.find_duplicate_aliases(undefined as unknown as Array<ShellConfigFile>);
shellconfigauditor.find_duplicates(undefined as unknown as Array<ShellConfigFile>);
shellconfigauditor.generate_consolidated(undefined as unknown as Array<ShellConfigFile>);
shellconfigauditor.sourcing_graph(undefined as unknown as Array<ShellConfigFile>);

// Create a ShellConfigFile instance
const shellconfigfile = new ShellConfigFile();
shellconfigfile.parse("example_path");

// Call audit
audit(undefined as unknown as any, undefined as unknown as Array<string>);
// Call check_sourcing_order
check_sourcing_order(undefined as unknown as any, undefined as unknown as Array<ShellConfigFile>);
// Call find_duplicate_aliases
find_duplicate_aliases(undefined as unknown as any, undefined as unknown as Array<ShellConfigFile>);
// Call find_duplicates
find_duplicates(undefined as unknown as any, undefined as unknown as Array<ShellConfigFile>);
// Call generate_consolidated
generate_consolidated(undefined as unknown as any, undefined as unknown as Array<ShellConfigFile>);
// Call parse
parse(undefined as unknown as any, "example_path");
// Call sourcing_graph
sourcing_graph(undefined as unknown as any, undefined as unknown as Array<ShellConfigFile>);
