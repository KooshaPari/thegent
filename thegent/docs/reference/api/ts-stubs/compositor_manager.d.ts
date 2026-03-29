// Auto-generated TypeScript declarations for compositor_manager
// Source: generate-api-docs.py

export declare class CompositorManager {
  constructor(layout: Layout);
  add_compositor(compositor: Compositor, slot_id: string, weight: number): void;
  focus(slot_id: string): void;
  get_compositor(slot_id: string): void;
  get_focused(): void;
  layout(): void;
  remove_compositor(slot_id: string): void;
  render_all(width: number): void;
  slot_ids(): void;
  switch_layout(layout: Layout): void;
}

export declare class CompositorSlot {
}

export declare class Layout extends Enum {
}

export declare function add_compositor(compositor: Compositor, slot_id: string, weight: number): void;
export declare function focus(slot_id: string): void;
export declare function get_compositor(slot_id: string): void;
export declare function get_focused(): void;
export declare function layout(): void;
export declare function remove_compositor(slot_id: string): void;
export declare function render_all(width: number): void;
export declare function slot_ids(): void;
export declare function switch_layout(layout: Layout): void;
