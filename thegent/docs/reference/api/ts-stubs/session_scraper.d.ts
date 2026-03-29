// Auto-generated TypeScript declarations for session_scraper
// Source: generate-api-docs.py

export declare class SessionScraper {
  constructor(project_root: string);
  collect_all_recent_prompts(): void;
  scrape_claude_history(): void;
  scrape_tmux_prompts(): void;
}

export declare function collect_all_recent_prompts(): void;
export declare function scrape_claude_history(): void;
export declare function scrape_tmux_prompts(): void;
