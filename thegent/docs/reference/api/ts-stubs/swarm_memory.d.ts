// Auto-generated TypeScript declarations for swarm_memory
// Source: generate-api-docs.py

export declare class SwarmMemoryConsolidator {
  constructor(swarm_id: string, local_memory: DualMemory);
  consolidate(peer_memories: Array<Record<(str, Any)>>): void;
}

export declare function consolidate(peer_memories: Array<Record<(str, Any)>>): void;
