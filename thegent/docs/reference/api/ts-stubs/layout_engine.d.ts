// Auto-generated TypeScript declarations for layout_engine
// Source: generate-api-docs.py

export declare class Direction extends StrEnum {
}

export declare class LayoutConstraints {
}

export declare class LayoutEngine {
  constructor();
  calculate_layout(width: number, height: number): void;
  create_grid(rows: number, cols: number, widget_ids: Array<string>): void;
  create_horizontal_stack(widget_ids: Array<string>, constraints: any): void;
  create_vertical_stack(widget_ids: Array<string>, constraints: any): void;
  generate_layout_css(): void;
  get_widget(widget_id: string): void;
  register_widget(widget_id: string, widget: object): void;
}

export declare class LayoutNode {
  constructor(direction: Direction, constraints: any);
  add_child(child: any, constraints: any): void;
  generate_css(indent: number): void;
  get_css_for_child(index: number): void;
  to_dict(): void;
}

export declare class Margin {
  to_textual_css(): void;
}

export declare class Padding {
  to_textual_css(): void;
}

export declare class Size {
  constructor(value: number, unit: any);
  to_textual_css(): void;
}

export declare class SizeUnit extends StrEnum {
}

export declare function add_child(child: any, constraints: any): void;
export declare function calculate_layout(width: number, height: number): void;
export declare function create_grid(rows: number, cols: number, widget_ids: Array<string>): void;
export declare function create_horizontal_stack(widget_ids: Array<string>, constraints: any): void;
export declare function create_vertical_stack(widget_ids: Array<string>, constraints: any): void;
export declare function generate_css(indent: number): void;
export declare function generate_layout_css(): void;
export declare function get_css_for_child(index: number): void;
export declare function get_widget(widget_id: string): void;
export declare function register_widget(widget_id: string, widget: object): void;
export declare function to_dict(): void;
export declare function to_textual_css(): void;
