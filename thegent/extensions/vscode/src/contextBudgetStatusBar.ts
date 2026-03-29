// @trace WL-117
// Status bar item showing context budget (e.g. "⚡ 45% context").
// Updates from RunResult.context_usage_ratio (0.0–1.0).

import * as vscode from "vscode";

// ─── Status bar item ──────────────────────────────────────────────────────────

export class ContextBudgetStatusBar {
  private readonly _item: vscode.StatusBarItem;
  private _ratio: number = 0;

  constructor() {
    this._item = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100,
    );
    this._item.command = "thegent.listSessions";
    this._item.tooltip = "thegent: context budget — click to list sessions";
    this._render();
  }

  show(): void {
    this._item.show();
  }

  hide(): void {
    this._item.hide();
  }

  /**
   * Update the displayed context budget ratio.
   * @param ratio A value in [0.0, 1.0] representing context used.
   */
  update(ratio: number): void {
    if (ratio < 0 || ratio > 1) {
      throw new RangeError(
        `ContextBudgetStatusBar.update: ratio must be in [0, 1], got ${ratio}`,
      );
    }
    this._ratio = ratio;
    this._render();
  }

  private _render(): void {
    const pct = Math.round(this._ratio * 100);
    const icon = this._iconForRatio(this._ratio);
    this._item.text = `${icon} ${pct}% context`;
    this._item.color = this._colorForRatio(this._ratio);
  }

  private _iconForRatio(ratio: number): string {
    if (ratio >= 0.9) {
      return "$(warning)";
    }
    if (ratio >= 0.7) {
      return "$(zap)";
    }
    return "$(circuit-board)";
  }

  private _colorForRatio(ratio: number): vscode.ThemeColor {
    if (ratio >= 0.9) {
      return new vscode.ThemeColor("statusBarItem.errorBackground");
    }
    if (ratio >= 0.7) {
      return new vscode.ThemeColor("statusBarItem.warningBackground");
    }
    return new vscode.ThemeColor("statusBar.foreground");
  }

  dispose(): void {
    this._item.dispose();
  }
}
