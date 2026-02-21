// @trace WL-117
// Webview panel for diff display + Approve/Reject buttons.
// Shown when `approval/requested` notification fires from agent-server.

import * as vscode from "vscode";
import { AgentServerClient, AgentServerProtocolError } from "./agentServerClient";
import { ApprovalRequestedParams } from "./types";

// ─── Message types (webview → extension) ─────────────────────────────────────

type WebviewMessage =
  | { type: "approve"; approvalId: string }
  | { type: "reject"; approvalId: string };

function isWebviewMessage(msg: unknown): msg is WebviewMessage {
  if (typeof msg !== "object" || msg === null) {
    return false;
  }
  const m = msg as Record<string, unknown>;
  return (
    (m["type"] === "approve" || m["type"] === "reject") &&
    typeof m["approvalId"] === "string"
  );
}

// ─── Panel ────────────────────────────────────────────────────────────────────

export class ApprovalWebviewPanel {
  private static _current: ApprovalWebviewPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;

  private constructor(
    panel: vscode.WebviewPanel,
    private readonly _params: ApprovalRequestedParams,
    private readonly _client: AgentServerClient,
  ) {
    this._panel = panel;
    this._panel.webview.html = this._buildHtml();
    this._panel.webview.onDidReceiveMessage((rawMsg: unknown) => {
      this._handleMessage(rawMsg);
    });
    this._panel.onDidDispose(() => {
      ApprovalWebviewPanel._current = undefined;
    });
  }

  static show(
    params: ApprovalRequestedParams,
    client: AgentServerClient,
    extensionUri: vscode.Uri,
  ): ApprovalWebviewPanel {
    // Only one approval panel at a time — reveal existing if any
    if (ApprovalWebviewPanel._current !== undefined) {
      ApprovalWebviewPanel._current._panel.reveal(vscode.ViewColumn.Two);
      return ApprovalWebviewPanel._current;
    }

    const panel = vscode.window.createWebviewPanel(
      "thegentApproval",
      `thegent: Approve — ${params.approval_id}`,
      { viewColumn: vscode.ViewColumn.Two, preserveFocus: false },
      {
        enableScripts: true,
        localResourceRoots: [extensionUri],
        retainContextWhenHidden: false,
      },
    );

    const instance = new ApprovalWebviewPanel(panel, params, client);
    ApprovalWebviewPanel._current = instance;
    return instance;
  }

  private _handleMessage(rawMsg: unknown): void {
    if (!isWebviewMessage(rawMsg)) {
      throw new Error(`ApprovalWebviewPanel: unexpected message shape: ${JSON.stringify(rawMsg)}`);
    }

    if (rawMsg.type === "approve") {
      void this._client.grantApproval(rawMsg.approvalId).then(() => {
        this._panel.dispose();
      }).catch((err: unknown) => {
        const msg = err instanceof AgentServerProtocolError ? err.message : String(err);
        void vscode.window.showErrorMessage(`thegent: approval/grant failed: ${msg}`);
        this._panel.dispose();
      });
    } else {
      void this._client.rejectApproval(rawMsg.approvalId).then(() => {
        this._panel.dispose();
      }).catch((err: unknown) => {
        const msg = err instanceof AgentServerProtocolError ? err.message : String(err);
        void vscode.window.showErrorMessage(`thegent: approval/reject failed: ${msg}`);
        this._panel.dispose();
      });
    }
  }

  private _buildHtml(): string {
    const approvalId = this._escapeHtml(this._params.approval_id);
    const sessionId = this._escapeHtml(this._params.session_id);
    const turnId = this._escapeHtml(this._params.turn_id);
    const diff = this._params.diff !== undefined
      ? this._escapeHtml(this._params.diff)
      : "(no diff payload — operation metadata only)";

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
  <title>thegent Approval</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background: var(--vscode-editor-background);
      padding: 16px;
    }
    h2 { margin-top: 0; }
    .meta { font-size: 0.85em; color: var(--vscode-descriptionForeground); margin-bottom: 12px; }
    pre {
      background: var(--vscode-textCodeBlock-background);
      border: 1px solid var(--vscode-panel-border);
      padding: 12px;
      overflow-x: auto;
      white-space: pre-wrap;
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
    .line-add { color: var(--vscode-gitDecoration-addedResourceForeground); }
    .line-remove { color: var(--vscode-gitDecoration-deletedResourceForeground); }
    .actions { margin-top: 16px; display: flex; gap: 8px; }
    button {
      padding: 8px 20px;
      border: none;
      cursor: pointer;
      font-size: 1em;
      border-radius: 2px;
    }
    .btn-approve {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
    }
    .btn-approve:hover { background: var(--vscode-button-hoverBackground); }
    .btn-reject {
      background: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }
    .btn-reject:hover { background: var(--vscode-button-secondaryHoverBackground); }
  </style>
</head>
<body>
  <h2>thegent: Approval Required</h2>
  <div class="meta">
    <div><strong>Approval ID:</strong> ${approvalId}</div>
    <div><strong>Session:</strong> ${sessionId}</div>
    <div><strong>Turn:</strong> ${turnId}</div>
  </div>
  <pre id="diff-content">${diff}</pre>
  <div class="actions">
    <button class="btn-approve" id="btn-approve">Approve</button>
    <button class="btn-reject" id="btn-reject">Reject</button>
  </div>
  <script>
    const vscode = acquireVsCodeApi();
    const approvalId = ${JSON.stringify(approvalId)};

    document.getElementById('btn-approve').addEventListener('click', function() {
      document.getElementById('btn-approve').disabled = true;
      document.getElementById('btn-reject').disabled = true;
      vscode.postMessage({ type: 'approve', approvalId: approvalId });
    });

    document.getElementById('btn-reject').addEventListener('click', function() {
      document.getElementById('btn-approve').disabled = true;
      document.getElementById('btn-reject').disabled = true;
      vscode.postMessage({ type: 'reject', approvalId: approvalId });
    });
  </script>
</body>
</html>`;
  }

  private _escapeHtml(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  dispose(): void {
    this._panel.dispose();
  }
}
