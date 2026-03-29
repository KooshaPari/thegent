// Auto-generated TypeScript declarations for fast_string_ops
// Source: generate-api-docs.py

export declare class FastStringOps {
  fuzzy_match(query: string, choices: Array<string>, limit: number, score_cutoff: number): void;
  fuzzy_ratio(str1: string, str2: string): void;
  regex_findall(pattern: string, text: string): void;
  regex_search(pattern: string, text: string): void;
}

export declare function fuzzy_match(query: string, choices: Array<string>, limit: number, score_cutoff: number): void;
export declare function fuzzy_ratio(str1: string, str2: string): void;
export declare function regex_findall(pattern: string, text: string): void;
export declare function regex_search(pattern: string, text: string): void;
