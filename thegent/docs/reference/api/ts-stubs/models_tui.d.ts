// Auto-generated TypeScript declarations for models_tui
// Source: generate-api-docs.py

export declare class ModelAddModal {
  compose(): void;
  on_button_pressed(event: Button.Pressed): void;
}

export declare class ModelsTUI extends App {
  constructor();
  action_add_model(): void;
  action_delete_model(): void;
  compose(): void;
  load_data(): void;
  on_button_pressed(event: Button.Pressed): void;
  on_mount(): void;
  refresh_list(): void;
  save_data(): void;
}

export declare function action_add_model(): void;
export declare function action_delete_model(): void;
export declare function compose(): ComposeResult;
export declare function handle_add(result: any): void;
export declare function load_data(): void;
export declare function models_tui_main(): void;
export declare function on_button_pressed(event: Button.Pressed): void;
export declare function on_mount(): void;
export declare function refresh_list(): void;
export declare function save_data(): void;
