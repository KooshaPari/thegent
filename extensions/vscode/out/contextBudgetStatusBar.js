"use strict";
// @trace WL-117
// Status bar item showing context budget (e.g. "⚡ 45% context").
// Updates from RunResult.context_usage_ratio (0.0–1.0).
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContextBudgetStatusBar = void 0;
const vscode = __importStar(require("vscode"));
// ─── Status bar item ──────────────────────────────────────────────────────────
class ContextBudgetStatusBar {
    constructor() {
        this._ratio = 0;
        this._item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this._item.command = "thegent.listSessions";
        this._item.tooltip = "thegent: context budget — click to list sessions";
        this._render();
    }
    show() {
        this._item.show();
    }
    hide() {
        this._item.hide();
    }
    /**
     * Update the displayed context budget ratio.
     * @param ratio A value in [0.0, 1.0] representing context used.
     */
    update(ratio) {
        if (ratio < 0 || ratio > 1) {
            throw new RangeError(`ContextBudgetStatusBar.update: ratio must be in [0, 1], got ${ratio}`);
        }
        this._ratio = ratio;
        this._render();
    }
    _render() {
        const pct = Math.round(this._ratio * 100);
        const icon = this._iconForRatio(this._ratio);
        this._item.text = `${icon} ${pct}% context`;
        this._item.color = this._colorForRatio(this._ratio);
    }
    _iconForRatio(ratio) {
        if (ratio >= 0.9) {
            return "$(warning)";
        }
        if (ratio >= 0.7) {
            return "$(zap)";
        }
        return "$(circuit-board)";
    }
    _colorForRatio(ratio) {
        if (ratio >= 0.9) {
            return new vscode.ThemeColor("statusBarItem.errorBackground");
        }
        if (ratio >= 0.7) {
            return new vscode.ThemeColor("statusBarItem.warningBackground");
        }
        return new vscode.ThemeColor("statusBar.foreground");
    }
    dispose() {
        this._item.dispose();
    }
}
exports.ContextBudgetStatusBar = ContextBudgetStatusBar;
//# sourceMappingURL=contextBudgetStatusBar.js.map