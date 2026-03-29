// Auto-generated TypeScript declarations for workstream_dashboard
// Source: generate-api-docs.py

export declare class ConcurrencyPanel extends Static {
  constructor();
  update_concurrency(running: number, limit: number): void;
}

export declare class DependenciesTable extends DataTable {
  constructor();
  update_dependencies(deps: Array<Record<(str, Any)>>): void;
}

export declare class GardenerPanel extends Static {
  constructor();
  update_health(health_data: Record<(str, Any)>): void;
}

export declare class KPIPanel extends Static {
  constructor();
  update_kpis(kpis: Record<(str, Any)>): void;
}

export declare class ReputationTable extends DataTable {
  constructor();
  update_scores(scores: Record<(str, float)>): void;
}

export declare class SessionsTable extends DataTable {
  constructor();
  update_sessions(sessions: Array<Record<(str, Any)>>): void;
}

export declare class StatsPanel extends Static {
  constructor();
  update_stats(stats: Record<(str, Any)>): void;
}

export declare class WorkstreamDashboard extends App {
  constructor();
  action_quit(): void;
  action_refresh(): void;
  compose(): void;
  on_mount(): void;
}

export declare class WorkstreamItemsTable extends DataTable {
  constructor();
  update_items(items: Array<Record<(str, Any)>>): void;
}

export declare class XPTable extends DataTable {
  constructor();
  update_xp(xp_data: Array<Record<(str, Any)>>): void;
}

export declare function action_quit(): void;
export declare function action_refresh(): void;
export declare function compose(): void;
export declare function on_mount(): void;
export declare function run_dashboard(): void;
export declare function update_concurrency(running: number, limit: number): void;
export declare function update_dependencies(deps: Array<Record<(str, Any)>>): void;
export declare function update_health(health_data: Record<(str, Any)>): void;
export declare function update_items(items: Array<Record<(str, Any)>>): void;
export declare function update_kpis(kpis: Record<(str, Any)>): void;
export declare function update_scores(scores: Record<(str, float)>): void;
export declare function update_sessions(sessions: Array<Record<(str, Any)>>): void;
export declare function update_stats(stats: Record<(str, Any)>): void;
export declare function update_xp(xp_data: Array<Record<(str, Any)>>): void;
