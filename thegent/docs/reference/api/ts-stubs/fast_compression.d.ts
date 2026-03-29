// Auto-generated TypeScript declarations for fast_compression
// Source: generate-api-docs.py

export declare class FastCompression {
  compress(data: Uint8Array, method: string, level: number): void;
  decompress(data: Uint8Array, method: any): void;
}

export declare function compress(data: Uint8Array, method: string, level: number): void;
export declare function decompress(data: Uint8Array, method: any): void;
