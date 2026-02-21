// Auto-generated TypeScript declarations for dialog
// Source: generate-api-docs.py

export declare class ConfirmDialog extends Dialog {
  constructor(message: string, title: string, yes_label: string, no_label: string);
}

export declare class Dialog extends Container {
  constructor(title: string);
  compose(): void;
  on_click(event: Click): void;
  on_key(event: Key): void;
  on_mount(): void;
  on_result(callback: Callable<(Any, None)>): void;
}

export declare class DialogManager {
  constructor();
  close_all(): void;
  show_confirm(message: string, title: string, on_result: any): void;
  show_dialog(dialog: Dialog): void;
  show_input(prompt: string, title: string, default: string, password: boolean, on_result: any): void;
  show_message(message: string, title: string, style: DialogStyle): void;
  show_toast(message: string, duration: number, style: DialogStyle): void;
}

export declare class DialogResult extends Enum {
}

export declare class DialogStyle extends Enum {
}

export declare class InputDialog extends Dialog {
  constructor(prompt: string, title: string, default: string, password: boolean, placeholder: string);
  get_value(): void;
}

export declare class MessageDialog extends Dialog {
  constructor(message: string, title: string);
}

export declare class Overlay extends Container {
  constructor();
}

export declare class Toast extends Container {
  constructor(message: string, duration: number, style: DialogStyle);
  compose(): void;
  dismiss(): void;
  on_mount(): void;
}

export declare function close_all(): void;
export declare function compose(): ComposeResult;
export declare function dismiss(): void;
export declare function get_value(): void;
export declare function on_click(event: Click): void;
export declare function on_key(event: Key): void;
export declare function on_mount(): void;
export declare function on_result(callback: Callable<(Any, None)>): void;
export declare function show_confirm(message: string, title: string, on_result: any): void;
export declare function show_dialog(dialog: Dialog): void;
export declare function show_input(prompt: string, title: string, default: string, password: boolean, on_result: any): void;
export declare function show_message(message: string, title: string, style: DialogStyle): void;
export declare function show_toast(message: string, duration: number, style: DialogStyle): void;
