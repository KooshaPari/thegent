// Auto-generated usage examples for session_scraper
// Source: generate-api-docs.py

import { SessionScraper, collect_all_recent_prompts, scrape_claude_history, scrape_tmux_prompts } from "./session_scraper";

// Create a SessionScraper instance
const sessionscraper = new SessionScraper("example_project_root");
sessionscraper.collect_all_recent_prompts();
sessionscraper.scrape_claude_history();
sessionscraper.scrape_tmux_prompts();

// Call collect_all_recent_prompts
collect_all_recent_prompts(undefined as unknown as any);
// Call scrape_claude_history
scrape_claude_history(undefined as unknown as any);
// Call scrape_tmux_prompts
scrape_tmux_prompts(undefined as unknown as any);
