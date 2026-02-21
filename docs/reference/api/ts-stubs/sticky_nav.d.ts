// Auto-generated TypeScript declarations for sticky_nav
// Source: generate-api-docs.py

export declare class StickyNav {
  constructor(sidebar: boolean, header: boolean);
  render_css(): void;
  render_html(sidebar_content: string, header_content: string): void;
}

export declare function render_css(): void;
export declare function render_html(sidebar_content: string, header_content: string): void;
