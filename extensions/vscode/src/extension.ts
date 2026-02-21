// @trace WL-117
// Main VS Code extension entry point — thegent agent-server MCP client + session UI.
// Connects via child_process.spawn('thegent', ['agent-server']) + stdout/stdin JSONL pipes.
// Fails fast: no fallback code paths. Surfaces all errors to the user.

import * as vscode from "vscode";
import { AgentServerClient, AgentServerConnectionError, AgentServerProtocolError } from "./agentServerClient";
import { SessionListProvider, SessionTreeItem } from "./sessionListProvider";
import { ContextBudgetStatusBar } from "./contextBudgetStatusBar";
import { ApprovalWebviewPanel } from "./approvalWebviewPanel";
import { ApprovalRequestedParams, RunResult } from "./types";

// ─── Extension state ──────────────────────────────────────────────────────────

let _client: AgentServerClient | undefined;
let _sessionProvider: SessionListProvider | undefined;
let _statusBar: ContextBudgetStatusBar | undefined;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getConfig(): { command: string; args: string[] } {
  const config = vscode.workspace.getConfiguration("thegent");
  const command = config.get<string>("agentServerCommand", "thegent");
  const args = config.get<string[]>("agentServerArgs", ["agent-server"]);
  return { command, args };
}

function requireClient(): AgentServerClient {
  if (_client === undefined) {
    throw new AgentServerConnectionError(
      "Not connected to thegent agent-server. Run 'thegent: Start New Session' first.",
    );
  }
  return _client;
}

function requireSessionProvider(): SessionListProvider {
  if (_sessionProvider === undefined) {
    throw new Error("SessionListProvider not initialized");
  }
  return _sessionProvider;
}

function connectClient(
  context: vscode.ExtensionContext,
  extensionUri: vscode.Uri,
): AgentServerClient {
  const { command, args } = getConfig();

  let client: AgentServerClient;
  try {
    client = AgentServerClient.spawn(command, args);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new AgentServerConnectionError(
      `Failed to spawn '${command} ${args.join(" ")}': ${msg}`,
    );
  }

  const provider = requireSessionProvider();
  provider.setClient(client);

  // Wire notifications
  client.on("approval/requested", (params: ApprovalRequestedParams) => {
    ApprovalWebviewPanel.show(params, client, extensionUri);
  });

  client.on("context/budgetUpdated", (result: RunResult) => {
    _statusBar?.update(result.context_usage_ratio);
  });

  client.on("disconnected", () => {
    void vscode.window.showWarningMessage(
      "thegent agent-server disconnected. Reconnect by starting a new session.",
    );
    _client = undefined;
  });

  // Surface stderr to output channel
  const outputChannel = vscode.window.createOutputChannel("thegent");
  context.subscriptions.push(outputChannel);

  client.stderr.on("data", (chunk: Buffer) => {
    outputChannel.append(chunk.toString("utf8"));
  });

  _client = client;
  return client;
}

// ─── Command handlers ─────────────────────────────────────────────────────────

async function cmdStart(
  context: vscode.ExtensionContext,
  extensionUri: vscode.Uri,
): Promise<void> {
  let client = _client;
  if (client === undefined) {
    client = connectClient(context, extensionUri);
  }

  const session = await client.startSession();
  await requireSessionProvider().fetchAndRefresh();
  void vscode.window.showInformationMessage(
    `thegent: session started — ${session.id}`,
  );
}

async function cmdListSessions(): Promise<void> {
  const client = requireClient();
  const sessions = await client.listSessions();
  requireSessionProvider().updateSessions(sessions);
}

async function cmdResume(item: unknown): Promise<void> {
  const client = requireClient();

  let sessionId: string;
  if (item instanceof SessionTreeItem) {
    sessionId = item.session.id;
  } else {
    const input = await vscode.window.showInputBox({
      prompt: "Enter session ID to resume",
      placeHolder: "session-0001",
    });
    if (input === undefined || input.trim() === "") {
      return;
    }
    sessionId = input.trim();
  }

  const session = await client.resumeSession(sessionId);
  await requireSessionProvider().fetchAndRefresh();
  void vscode.window.showInformationMessage(
    `thegent: resumed session ${session.id} (status: ${session.status})`,
  );
}

// ─── Activate ─────────────────────────────────────────────────────────────────

export function activate(context: vscode.ExtensionContext): void {
  const provider = new SessionListProvider();
  _sessionProvider = provider;

  const statusBar = new ContextBudgetStatusBar();
  _statusBar = statusBar;
  statusBar.show();

  // Register tree view
  const treeView = vscode.window.createTreeView("thegentSessions", {
    treeDataProvider: provider,
    showCollapseAll: false,
  });

  context.subscriptions.push(treeView);
  context.subscriptions.push(statusBar);
  context.subscriptions.push({ dispose: () => provider.dispose() });

  // Register commands
  const startCmd = vscode.commands.registerCommand("thegent.start", () => {
    void cmdStart(context, context.extensionUri).catch((err: unknown) => {
      const msg =
        err instanceof AgentServerConnectionError ||
        err instanceof AgentServerProtocolError
          ? err.message
          : String(err);
      void vscode.window.showErrorMessage(`thegent: ${msg}`);
    });
  });

  const listCmd = vscode.commands.registerCommand("thegent.listSessions", () => {
    void cmdListSessions().catch((err: unknown) => {
      const msg =
        err instanceof AgentServerConnectionError ||
        err instanceof AgentServerProtocolError
          ? err.message
          : String(err);
      void vscode.window.showErrorMessage(`thegent: ${msg}`);
    });
  });

  const resumeCmd = vscode.commands.registerCommand(
    "thegent.resume",
    (item: unknown) => {
      void cmdResume(item).catch((err: unknown) => {
        const msg =
          err instanceof AgentServerConnectionError ||
          err instanceof AgentServerProtocolError
            ? err.message
            : String(err);
        void vscode.window.showErrorMessage(`thegent: ${msg}`);
      });
    },
  );

  // Legacy scaffold commands (keep for backwards compat with existing test assertions)
  const startSessionCmd = vscode.commands.registerCommand(
    "thegent.startSession",
    () => {
      void cmdStart(context, context.extensionUri).catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        void vscode.window.showErrorMessage(`thegent: ${msg}`);
      });
    },
  );

  const submitTurnCmd = vscode.commands.registerCommand(
    "thegent.submitTurn",
    () => {
      void (async () => {
        const client = requireClient();
        const sessions = await client.listSessions();
        if (sessions.length === 0) {
          void vscode.window.showErrorMessage("thegent: no active sessions — start one first");
          return;
        }
        const sessionId = sessions[sessions.length - 1].id;
        const input = await vscode.window.showInputBox({
          prompt: `Submit turn to session ${sessionId}`,
          placeHolder: "Enter your prompt",
        });
        if (input === undefined || input.trim() === "") {
          return;
        }
        await client.submitTurn(sessionId, input.trim());
        await provider.fetchAndRefresh();
      })().catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        void vscode.window.showErrorMessage(`thegent: ${msg}`);
      });
    },
  );

  const showSessionsCmd = vscode.commands.registerCommand(
    "thegent.showSessions",
    () => {
      void cmdListSessions().catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        void vscode.window.showErrorMessage(`thegent: ${msg}`);
      });
    },
  );

  context.subscriptions.push(
    startCmd,
    listCmd,
    resumeCmd,
    startSessionCmd,
    submitTurnCmd,
    showSessionsCmd,
  );
}

// ─── Deactivate ───────────────────────────────────────────────────────────────

export function deactivate(): void {
  _client?.dispose();
  _client = undefined;
  _sessionProvider = undefined;
  _statusBar = undefined;
}
