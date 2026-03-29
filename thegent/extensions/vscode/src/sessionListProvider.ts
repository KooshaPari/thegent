// @trace WL-117
// TreeDataProvider for the thegent Sessions side panel.
// Displays sessions with status icons and supports inline Resume command.

import * as vscode from "vscode";
import { AgentServerClient } from "./agentServerClient";
import { Session, SessionStatus } from "./types";

// ─── Tree item ────────────────────────────────────────────────────────────────

export class SessionTreeItem extends vscode.TreeItem {
  constructor(public readonly session: Session) {
    super(
      `${session.id} (${session.status})`,
      vscode.TreeItemCollapsibleState.None,
    );
    this.contextValue = "session";
    this.tooltip = `Session: ${session.id}\nStatus: ${session.status}\nTurns: ${session.turn_ids.length}`;
    this.iconPath = SessionTreeItem._iconForStatus(session.status);
    this.description = `${session.turn_ids.length} turn(s)`;
  }

  private static _iconForStatus(status: SessionStatus): vscode.ThemeIcon {
    switch (status) {
      case "active":
        return new vscode.ThemeIcon("sync~spin", new vscode.ThemeColor("charts.green"));
      case "paused":
        return new vscode.ThemeIcon("debug-pause", new vscode.ThemeColor("charts.yellow"));
      case "completed":
        return new vscode.ThemeIcon("check", new vscode.ThemeColor("charts.blue"));
      case "failed":
        return new vscode.ThemeIcon("error", new vscode.ThemeColor("charts.red"));
    }
  }
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export class SessionListProvider
  implements vscode.TreeDataProvider<SessionTreeItem>
{
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<
    SessionTreeItem | undefined | null | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private _sessions: Session[] = [];
  private _client: AgentServerClient | undefined = undefined;

  setClient(client: AgentServerClient): void {
    this._client = client;
  }

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  async fetchAndRefresh(): Promise<void> {
    if (this._client === undefined) {
      throw new Error("SessionListProvider: no client set — call setClient() first");
    }
    this._sessions = await this._client.listSessions();
    this.refresh();
  }

  updateSessions(sessions: Session[]): void {
    this._sessions = sessions;
    this.refresh();
  }

  getTreeItem(element: SessionTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(_element?: SessionTreeItem): SessionTreeItem[] {
    // Flat list — no nested children for sessions
    return this._sessions.map((s) => new SessionTreeItem(s));
  }

  dispose(): void {
    this._onDidChangeTreeData.dispose();
  }
}
