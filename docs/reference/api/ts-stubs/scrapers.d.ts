// Auto-generated TypeScript declarations for scrapers
// Source: generate-api-docs.py

export declare class ModelScraper extends Protocol {
}

export declare function get_models_cache_path(): void;
export declare function get_scraped_catalog(use_cache: boolean, refresh: boolean, settings: any): void;
export declare function invalidate_models_cache(): void;
export declare function scrape_all(settings: any): void;
export declare function scrape_claude(): void;
export declare function scrape_copilot(): void;
export declare function scrape_cursor(): void;
export declare function scrape_cursor_api(settings: any): void;
export declare function scrape_gemini(): void;
export declare function scrape_minimax_from_proxy(): void;
export declare function scrape_proxy(settings: any): void;
