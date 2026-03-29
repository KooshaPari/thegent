export type AuthStatus = 'pending' | 'authenticated' | 'unauthenticated';

export interface AwsCreds {
  accessKeyId: string;
  secretAccessKey: string;
}

export interface Portfolio {
  rootEndpoint: string;
  apiKey: string;
}

export interface LLMProvider {
  modal: string;
  apiKey: string;
  baseUrl?: string;
}

export interface LLMConfig {
  provider: string;
  providers: Record<string, LLMProvider>;
}

export interface RawAwsCreds {
  AccessKeyID?: string;
  SecretAccessKey?: string;
}

export interface RawPortfolio {
  RootEndpoint?: string;
  APIKey?: string;
}

export interface RawLLMProvider {
  Modal?: string;
  APIKey?: string;
}

export interface RawLLMConfig {
  Provider?: string;
  Providers?: Record<string, RawLLMProvider>;
}

export interface User {
  uuid: string;
  name: string;
  email: string;
  awsCreds?: AwsCreds;
  AwsCreds?: RawAwsCreds;
  portfolio?: Portfolio;
  Portfolio?: RawPortfolio;
  llmConfig?: LLMConfig;
  LLMConfig?: RawLLMConfig;
}

export interface ProjectInstanceResource {
  id: string;
  type: string;
  name: string;
  arn: string;
  status: string;
  region: string;
  service: string;
}

export interface ProjectInstance {
  uuid: string;
  name: string;
  status: string;
  resources: ProjectInstanceResource[];
  rootProjectUUID: string;
  lastUpdated: string;
}

export interface Project {
  uuid: string;
  name: string;
  description: string;
  access_url: string;
  deployments?: Record<string, ProjectInstance>;
}

export interface NormalizedUser {
  uuid: string;
  name: string;
  email: string;
  awsCreds?: AwsCreds;
  portfolio?: Portfolio;
  llmConfig?: LLMConfig;
}

export interface AuthState {
  status: AuthStatus;
  user: NormalizedUser | null;
}

export interface InstanceResource {
  ID?: string;
  id?: string;
  type?: string;
  Type?: string;
  name?: string;
  Name?: string;
  arn?: string;
  ARN?: string;
  status?: string;
  Status?: string;
  region?: string;
  Region?: string;
  service?: string;
  Service?: string;
}

export interface InstanceRecord {
  uuid: string;
  UUID?: string;
  name: string;
  Name?: string;
  status: string;
  Status?: string;
  resUUID?: string;
  ResUUID?: string;
  resources?: InstanceResource[];
  Resources?: InstanceResource[];
}

export interface NormalizedInstanceRecord {
  uuid: string;
  name: string;
  status: string;
  resources: InstanceResource[];
}

export interface UserCredentials {
  uuid: string;
  name: string;
  email: string;
  awsCreds: AwsCreds;
  llmConfig: LLMConfig;
  portfolio: Portfolio;
}

export interface UserSecretsUpdateRequest {
  UUID: string;
  Name: string;
  Email: string;
  AwsCreds: {
    accessKeyId: string;
    secretAccessKey: string;
  };
  LLMConfig: {
    provider: string;
    providers: Record<string, { modal: string; apiKey: string }>;
  };
  Portfolio: {
    rootEndpoint: string;
    apiKey: string;
  };
}

export interface UserProfileUpdateRequest {
  Name?: string;
  Email?: string;
  Password?: string;
}

// ============================================================================
// Deployment Types
// ============================================================================

export type DeploymentStatus =
  | 'pending'
  | 'building'
  | 'deploying'
  | 'running'
  | 'failed'
  | 'terminated';

export type AppType = 'frontend' | 'backend' | 'database' | 'static' | 'container';

export interface DeployRequest {
  name: string;
  type: AppType;
  provider?: ProviderName;
  git_url?: string;
  branch?: string;
  env_vars?: Record<string, string>;
  config?: Record<string, any>;
  runtime?: string;
  build_command?: string;
  start_command?: string;
  install_command?: string;
  framework?: string;
}

export interface Deployment {
  id: string;
  name: string;
  type: AppType;
  provider: ProviderName;
  status: DeploymentStatus;
  url?: string;
  git_url?: string;
  branch?: string;
  runtime?: string;
  framework?: string;
  env_vars?: Record<string, string>;
  build_logs?: string[];
  error_message?: string;
  created_at: string;
  updated_at: string;
  terminated_at?: string;
  metadata?: Record<string, any>;
}

export interface DeploymentResponse {
  id: string;
  name: string;
  status: DeploymentStatus;
  url?: string;
  provider: ProviderName;
  created_at: string;
  message: string;
}

export interface DeploymentStatusUpdate {
  id: string;
  status: DeploymentStatus;
  progress: number;
  message?: string;
  updated_at: string;
}

// ============================================================================
// Log Types
// ============================================================================

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';

export interface LogEntry {
  id?: string;
  deployment_id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  source?: 'build' | 'runtime' | 'system';
  metadata?: Record<string, any>;
}

export interface LogStreamEvent {
  type: 'log' | 'status' | 'error' | 'complete';
  data: LogEntry | DeploymentStatusUpdate | { message: string };
}

// ============================================================================
// Metrics Types
// ============================================================================

export interface MetricDataPoint {
  timestamp: string;
  value: number;
}

export interface Metrics {
  deployment_id: string;
  cpu_usage: MetricDataPoint[];
  memory_usage: MetricDataPoint[];
  network_in: MetricDataPoint[];
  network_out: MetricDataPoint[];
  request_count?: MetricDataPoint[];
  error_rate?: MetricDataPoint[];
  response_time?: MetricDataPoint[];
  timestamp: string;
}

export interface MetricsQuery {
  deployment_id: string;
  metric_type?: 'cpu' | 'memory' | 'network' | 'requests';
  start_time?: string;
  end_time?: string;
  interval?: '1m' | '5m' | '15m' | '1h' | '1d';
}

// ============================================================================
// Provider Types
// ============================================================================

export type ProviderName = 'vercel' | 'netlify' | 'render' | 'railway' | 'fly' | 'aws' | 'gcp' | 'azure' | 'supabase';

export type ProviderStatus = 'connected' | 'disconnected' | 'error' | 'pending';

export interface Provider {
  name: ProviderName;
  display_name: string;
  status: ProviderStatus;
  is_configured: boolean;
  capabilities: string[];
  regions?: string[];
  pricing_tier?: 'free' | 'hobby' | 'pro' | 'enterprise';
  credentials?: Record<string, any>;
  metadata?: {
    account_id?: string;
    email?: string;
    organization?: string;
    last_sync?: string;
  };
}

export interface ProviderConfig {
  name: ProviderName;
  api_key?: string;
  api_token?: string;
  access_token?: string;
  team_id?: string;
  organization_id?: string;
  project_id?: string;
  credentials?: Record<string, any>;
}

// ============================================================================
// Host Types
// ============================================================================

export type HostStatus = 'online' | 'offline' | 'degraded' | 'maintenance';

export interface Host {
  id: string;
  name: string;
  hostname: string;
  ip_address?: string;
  status: HostStatus;
  provider: ProviderName;
  region: string;
  cpu_cores?: number;
  memory_mb?: number;
  disk_gb?: number;
  os?: string;
  tags?: string[];
  created_at: string;
  last_seen?: string;
  metadata?: Record<string, any>;
}

export interface HostConfig {
  name: string;
  hostname: string;
  provider: ProviderName;
  region: string;
  ssh_key?: string;
  credentials?: Record<string, any>;
  tags?: string[];
}

// ============================================================================
// Cost Types
// ============================================================================

export interface CostEstimate {
  deployment_type: AppType;
  provider: ProviderName;
  estimated_monthly_cost: number;
  estimated_hourly_cost: number;
  currency: string;
  breakdown: {
    compute?: number;
    storage?: number;
    network?: number;
    additional?: number;
  };
  notes?: string[];
}

export interface CostData {
  total_cost: number;
  currency: string;
  period_start: string;
  period_end: string;
  deployments: Array<{
    id: string;
    name: string;
    provider: ProviderName;
    cost: number;
    usage_hours: number;
  }>;
  by_provider: Record<ProviderName, number>;
  trend?: 'increasing' | 'decreasing' | 'stable';
  projected_monthly_cost?: number;
}

// ============================================================================
// Detection Types
// ============================================================================

export interface DetectionResult {
  detected: boolean;
  framework?: string;
  runtime?: string;
  app_type?: AppType;
  confidence: number;
  suggested_config?: {
    build_command?: string;
    start_command?: string;
    install_command?: string;
    framework?: string;
    runtime?: string;
    env_vars?: Record<string, string>;
  };
  files_analyzed: string[];
  notes?: string[];
}

// ============================================================================
// Stats Types
// ============================================================================

export interface Stats {
  total_deployments: number;
  active_deployments: number;
  failed_deployments: number;
  total_requests: number;
  avg_response_time: number;
  uptime_percentage: number;
  total_cost: number;
  cost_trend: 'up' | 'down' | 'stable';
  deployments_by_status: Record<DeploymentStatus, number>;
  deployments_by_provider: Record<ProviderName, number>;
  recent_deployments: Deployment[];
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  error: string;
  message: string;
  code?: string;
  details?: any;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: string;
}

// ============================================================================
// Settings Types
// ============================================================================

export interface UserSettings {
  email_notifications: boolean;
  marketing_emails: boolean;
  deployment_alerts: boolean;
  weekly_reports: boolean;
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
}

export interface ApiKeyData {
  id: string;
  name: string;
  key: string;
  scopes: string[];
  created_at: string;
  last_used?: string;
  usage_count?: number;
  is_active: boolean;
}

export interface CreateApiKeyRequest {
  name: string;
  scopes: string[];
  expires_in?: number;
}

export interface CreateApiKeyResponse {
  id: string;
  key: string;
  name: string;
  scopes: string[];
  created_at: string;
  message: string;
}

export interface UsageStatistics {
  api_key_id: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  last_24h_requests: number;
  last_7d_requests: number;
  last_30d_requests: number;
  bandwidth_used: number;
}

export interface BillingPlan {
  id: string;
  name: string;
  tier: 'free' | 'hobby' | 'pro' | 'enterprise';
  price: number;
  currency: string;
  billing_period: 'monthly' | 'annual';
  features: string[];
  limits: {
    deployments: number;
    api_calls: number;
    bandwidth_gb: number;
    storage_gb: number;
    team_members: number;
  };
}

export interface BillingUsage {
  current_period_start: string;
  current_period_end: string;
  total_cost: number;
  currency: string;
  deployments_used: number;
  api_calls_used: number;
  bandwidth_gb_used: number;
  storage_gb_used: number;
  breakdown: {
    compute: number;
    storage: number;
    bandwidth: number;
    api_calls: number;
  };
}

export interface BillingHistory {
  id: string;
  period_start: string;
  period_end: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed' | 'refunded';
  invoice_url?: string;
  created_at: string;
}
