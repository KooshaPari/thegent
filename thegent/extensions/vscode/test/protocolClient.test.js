const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

function read(relativePath) {
  const absolutePath = path.join(__dirname, "..", relativePath);
  return fs.readFileSync(absolutePath, "utf8");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const clientSource = read("src/protocol/client.ts");
const typesSource = read("src/types.ts");
const extensionSource = read("src/extension.ts");
const contractDoc = read("docs/protocol-contract.md");
const readme = read("README.md");
const packageJson = JSON.parse(read("package.json"));
const contributedCommands = packageJson.contributes.commands.map((command) => command.command);

assert.match(clientSource, /PROTOCOL_METHODS/);
assert.match(typesSource, /health\/check/);
assert.match(typesSource, /config\/read/);
assert.match(typesSource, /session\/start/);
assert.match(typesSource, /turn\/submit/);

assert.ok(Array.isArray(packageJson.activationEvents));
const requiredCommands = ["thegent.startSession", "thegent.submitTurn", "thegent.showSessions"];
for (const command of requiredCommands) {
  assert.ok(contributedCommands.includes(command));
}
for (const command of contributedCommands) {
  assert.match(
    extensionSource,
    new RegExp(`registerCommand\\(\\s*"${escapeRegExp(command)}"`),
  );
  assert.ok(packageJson.activationEvents.includes(`onCommand:${command}`));
}

assert.match(contractDoc, /JSON-RPC 2\.0 over stdio/);
assert.match(contractDoc, /approval\/requested/);
assert.match(readme, /npm run lint/);
assert.match(readme, /npm run test/);

console.log("protocolClient scaffold checks passed");
