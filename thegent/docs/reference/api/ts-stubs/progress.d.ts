// Auto-generated TypeScript declarations for progress
// Source: generate-api-docs.py

export declare function decorator(func: any): void;
export declare function measure_time(description: string): void;
export declare function print_section(title: string): void;
export declare function print_status(message: string, status: string): void;
export declare function print_step(step: number, total: number, message: string): void;
export declare function progress_context(description: string, total: any, show_eta: boolean, show_speed: boolean): void;
export declare function spinner_context(message: string): void;
export declare function wrapper(): void;
