// Auto-generated TypeScript declarations for mojo_bridge
// Source: generate-api-docs.py

export declare class MojoBridge {
  constructor(mojo_root: any, cache_root: any);
  install_instructions(): void;
  is_available(): void;
}

export declare class MojoModule {
}

export declare class MojoNotAvailableError extends Exception {
}

export declare class MojoTask {
}

export declare function get_bridge(): void;
export declare function install_instructions(): void;
export declare function is_available(): void;
