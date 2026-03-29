'use client';

import { getApiBaseUrl, getDeploymentApiBaseUrl } from './config';
import type {
  InstanceRecord,
  NormalizedUser,
  Project,
  User,
  UserCredentials,
  UserProfileUpdateRequest,
  UserSecretsUpdateRequest,
  Deployment,
  DeployRequest,
  DeploymentResponse,
  DeploymentStatusUpdate,
  LogEntry,
  LogLevel,
  Metrics,
  MetricsQuery,
  Provider,
  ProviderConfig,
  Host,
  HostConfig,
  CostData,
  CostEstimate,
  DetectionResult,
  Stats,
  ApiError
} from './types';

import type { WorkOSCallbackPayload } from './authkit';
import { normalizeUser } from './normalizers';

// Re-export all types for convenience
export type {
  ApiError,
  AppType,
  CostData,
  CostEstimate,
  DeployRequest,
  Deployment,
  DeploymentResponse,
  DeploymentStatus,
  DeploymentStatusUpdate,
  DetectionResult,
  Host,
  HostConfig,
  InstanceRecord,
  LogEntry,
  LogLevel,
  MetricDataPoint,
  Metrics,
  MetricsQuery,
  NormalizedUser,
  Project,
  Provider,
  ProviderConfig,
  ProviderName,
  ProviderStatus,
  Stats,
  User,
  UserCredentials,
  UserProfileUpdateRequest,
  UserSecretsUpdateRequest
} from './types';

// ============================================================================
// Error Handling
// ============================================================================

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

export class NetworkError extends ApiClientError {
  constructor(message: string, details?: any) {
    super(message, undefined, 'NETWORK_ERROR', details);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends ApiClientError {
  constructor(message: string, details?: any) {
    super(message, 400, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends ApiClientError {
  constructor(message: string = 'Authentication required') {
    super(message, 401, 'AUTHENTICATION_ERROR');
    this.name = 'AuthenticationError';
  }
}

export class NotFoundError extends ApiClientError {
  constructor(message: string = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
    this.name = 'NotFoundError';
  }
}

// ============================================================================
// Retry Configuration
// ============================================================================

interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryableStatuses: number[];
  shouldRetry?: (error: any, attempt: number) => boolean;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
  shouldRetry: (error, attempt) => {
    if (attempt >= DEFAULT_RETRY_CONFIG.maxRetries) return false;
    if (error instanceof NetworkError) return true;
    if (error instanceof ApiClientError && error.status) {
      return DEFAULT_RETRY_CONFIG.retryableStatuses.includes(error.status);
    }
    return false;
  }
};

// ============================================================================
// Request Utilities
// ============================================================================

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function retryRequest<T>(
  fn: () => Promise<T>,
  config: RetryConfig = DEFAULT_RETRY_CONFIG,
  attempt: number = 0
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (config.shouldRetry && config.shouldRetry(error, attempt)) {
      const delay = config.retryDelay * Math.pow(2, attempt); // Exponential backoff
      await sleep(delay);
      return retryRequest(fn, config, attempt + 1);
    }
    throw error;
  }
}

// ============================================================================
// Core Request Function
// ============================================================================

async function request<T>(
  input: RequestInfo,
  init?: RequestInit,
  retry: boolean = true
): Promise<T> {
  const executeRequest = async (): Promise<T> => {
    try {
      const response = await fetch(input, {
        ...init,
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(init?.headers ?? {})
        }
      });

      // Handle different status codes
      if (response.status === 401) {
        throw new AuthenticationError();
      }

      if (response.status === 404) {
        throw new NotFoundError();
      }

      if (!response.ok) {
        const contentType = response.headers.get('Content-Type');
        let errorData: ApiError | null = null;

        try {
          if (contentType?.includes('application/json')) {
            errorData = await response.json();
          } else {
            const text = await response.text();
            errorData = { error: 'Request failed', message: text || `Status ${response.status}` };
          }
        } catch {
          errorData = { error: 'Request failed', message: `Status ${response.status}` };
        }

        throw new ApiClientError(
          errorData?.message || 'Request failed',
          response.status,
          errorData?.code,
          errorData?.details
        );
      }

      // Handle successful responses
      if (response.status === 204) {
        return undefined as T;
      }

      const contentType = response.headers.get('Content-Type');
      if (contentType?.includes('application/json')) {
        return response.json() as Promise<T>;
      }

      return undefined as T;
    } catch (error) {
      // Convert network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Network request failed', error);
      }
      throw error;
    }
  };

  if (retry) {
    return retryRequest(executeRequest);
  }
  return executeRequest();
}

export async function login(email: string, password: string): Promise<User> {
  const baseUrl = getApiBaseUrl();
  const result = await request<{ user: User }>(`${baseUrl}/login`, {
    method: 'POST',
    body: JSON.stringify({ Email: email, Password: password })
  });
  return result.user;
}

export async function signup(name: string, email: string, password: string): Promise<User> {
  const baseUrl = getApiBaseUrl();
  const result = await request<User>(`${baseUrl}/signup`, {
    method: 'POST',
    body: JSON.stringify({ Name: name, Email: email, Password: password })
  });
  return result;
}

export async function fetchAuthenticatedUser(): Promise<User> {
  const baseUrl = getApiBaseUrl();
  const result = await request<{ User: User }>(`${baseUrl}/authenticate`, {
    method: 'GET'
  });
  return result.User;
}

export async function logout(): Promise<void> {
  const baseUrl = getApiBaseUrl();
  try {
    await request<void>(`${baseUrl}/logout`, {
      method: 'POST'
    });
  } catch (error) {
    // If the server rejects the logout request we still clear client state
    if (error instanceof ApiClientError && (error.status === 401 || error.status === 404)) {
      return;
    }
    throw error;
  }
}

export async function fetchProjects(): Promise<Project[]> {
  const baseUrl = getApiBaseUrl();
  return request<Project[]>(`${baseUrl}/projects`, {
    method: 'GET'
  });
}

export async function fetchInstances(): Promise<InstanceRecord[]> {
  const baseUrl = getApiBaseUrl();
  return request<InstanceRecord[]>(`${baseUrl}/instances`, {
    method: 'GET'
  });
}

export async function completeWorkosCallback(payload: WorkOSCallbackPayload): Promise<void> {
  const baseUrl = getApiBaseUrl();
  await request<void>(`${baseUrl}/auth/workos/callback`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function fetchUserCredentials(userId: string): Promise<UserCredentials> {
  const baseUrl = getApiBaseUrl();
  const raw = await request<User>(`${baseUrl}/user/${userId}/creds`, {
    method: 'GET'
  });
  const normalized: NormalizedUser = normalizeUser(raw);
  return {
    uuid: normalized.uuid,
    name: normalized.name,
    email: normalized.email,
    awsCreds: normalized.awsCreds ?? { accessKeyId: '', secretAccessKey: '' },
    llmConfig: normalized.llmConfig ?? { provider: 'ollama', providers: {} },
    portfolio: normalized.portfolio ?? { rootEndpoint: '', apiKey: '' }
  };
}

export async function updateUserCredentials(payload: UserSecretsUpdateRequest): Promise<void> {
  const baseUrl = getApiBaseUrl();
  await request<void>(`${baseUrl}/link`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function updateUserProfile(
  userId: string,
  payload: UserProfileUpdateRequest
): Promise<User> {
  const baseUrl = getApiBaseUrl();
  return request<User>(`${baseUrl}/user/${userId}/creds`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  });
}

// ============================================================================
// API Configuration
// ============================================================================

const DEPLOYMENT_API_URL = getDeploymentApiBaseUrl();

// ============================================================================
// SSE (Server-Sent Events) Support
// ============================================================================

export interface SSEOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export function createEventSource(url: string, options: SSEOptions = {}): EventSource {
  const eventSource = new EventSource(url, { withCredentials: true });

  if (options.onOpen) {
    eventSource.addEventListener('open', options.onOpen);
  }

  if (options.onMessage) {
    eventSource.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        options.onMessage!(data);
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    });
  }

  if (options.onError) {
    eventSource.addEventListener('error', options.onError);
  }

  return eventSource;
}

// ============================================================================
// BytePort Deployment API
// ============================================================================

export async function deployApp(deploymentReq: DeployRequest): Promise<DeploymentResponse> {
  return request<DeploymentResponse>(`${DEPLOYMENT_API_URL}/deployments`, {
    method: 'POST',
    body: JSON.stringify(deploymentReq)
  });
}

export async function listDeployments(): Promise<{ deployments: Deployment[]; total: number }> {
  return request<{ deployments: Deployment[]; total: number }>(`${DEPLOYMENT_API_URL}/deployments`, {
    method: 'GET'
  });
}

export async function getDeployment(id: string): Promise<Deployment> {
  return request<Deployment>(`${DEPLOYMENT_API_URL}/deployments/${id}`, {
    method: 'GET'
  });
}

export async function getDeploymentStatus(id: string): Promise<DeploymentStatusUpdate> {
  return request<DeploymentStatusUpdate>(`${DEPLOYMENT_API_URL}/deployments/${id}/status`, {
    method: 'GET'
  });
}

export async function terminateDeployment(id: string): Promise<{ message: string; id: string }> {
  return request<{ message: string; id: string }>(`${DEPLOYMENT_API_URL}/deployments/${id}`, {
    method: 'DELETE'
  });
}

export async function updateDeployment(
  id: string,
  updates: Partial<DeployRequest>
): Promise<Deployment> {
  return request<Deployment>(`${DEPLOYMENT_API_URL}/deployments/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates)
  });
}

export async function restartDeployment(id: string): Promise<{ message: string; id: string }> {
  return request<{ message: string; id: string }>(`${DEPLOYMENT_API_URL}/deployments/${id}/restart`, {
    method: 'POST'
  });
}

// ============================================================================
// Logs API
// ============================================================================

export async function getDeploymentLogs(id: string): Promise<{ deployment_id: string; logs: LogEntry[] }> {
  return request<{ deployment_id: string; logs: LogEntry[] }>(`${DEPLOYMENT_API_URL}/deployments/${id}/logs`, {
    method: 'GET'
  });
}

export function streamDeploymentLogs(
  id: string,
  onLog: (log: LogEntry) => void,
  onError?: (error: Event) => void
): EventSource {
  return createEventSource(`${DEPLOYMENT_API_URL}/deployments/${id}/logs/stream`, {
    onMessage: onLog,
    onError
  });
}

export function streamDeploymentStatus(
  id: string,
  onStatusUpdate: (status: DeploymentStatusUpdate) => void,
  onError?: (error: Event) => void
): EventSource {
  return createEventSource(`${DEPLOYMENT_API_URL}/deployments/${id}/status/stream`, {
    onMessage: onStatusUpdate,
    onError
  });
}

// ============================================================================
// Metrics API
// ============================================================================

export async function getDeploymentMetrics(id: string, query?: MetricsQuery): Promise<Metrics> {
  const params = new URLSearchParams();
  if (query?.metric_type) params.set('type', query.metric_type);
  if (query?.start_time) params.set('start', query.start_time);
  if (query?.end_time) params.set('end', query.end_time);
  if (query?.interval) params.set('interval', query.interval);

  const queryString = params.toString();
  const url = `${DEPLOYMENT_API_URL}/deployments/${id}/metrics${queryString ? `?${queryString}` : ''}`;

  return request<Metrics>(url, { method: 'GET' });
}

export function streamDeploymentMetrics(
  id: string,
  onMetrics: (metrics: Metrics) => void,
  onError?: (error: Event) => void
): EventSource {
  return createEventSource(`${DEPLOYMENT_API_URL}/deployments/${id}/metrics/stream`, {
    onMessage: onMetrics,
    onError
  });
}

// ============================================================================
// Providers API
// ============================================================================

export async function getProviders(): Promise<Provider[]> {
  return request<Provider[]>(`${DEPLOYMENT_API_URL}/providers`, {
    method: 'GET'
  });
}

export async function getProvider(name: string): Promise<Provider> {
  return request<Provider>(`${DEPLOYMENT_API_URL}/providers/${name}`, {
    method: 'GET'
  });
}

export async function connectProvider(config: ProviderConfig): Promise<Provider> {
  return request<Provider>(`${DEPLOYMENT_API_URL}/providers`, {
    method: 'POST',
    body: JSON.stringify(config)
  });
}

export async function updateProvider(name: string, config: Partial<ProviderConfig>): Promise<Provider> {
  return request<Provider>(`${DEPLOYMENT_API_URL}/providers/${name}`, {
    method: 'PATCH',
    body: JSON.stringify(config)
  });
}

export async function disconnectProvider(name: string): Promise<{ message: string }> {
  return request<{ message: string }>(`${DEPLOYMENT_API_URL}/providers/${name}`, {
    method: 'DELETE'
  });
}

export async function testProviderConnection(name: string): Promise<{ connected: boolean; message?: string }> {
  return request<{ connected: boolean; message?: string }>(
    `${DEPLOYMENT_API_URL}/providers/${name}/test`,
    { method: 'POST' }
  );
}

// ============================================================================
// Hosts API
// ============================================================================

export async function getHosts(): Promise<Host[]> {
  return request<Host[]>(`${DEPLOYMENT_API_URL}/hosts`, {
    method: 'GET'
  });
}

export async function getHost(id: string): Promise<Host> {
  return request<Host>(`${DEPLOYMENT_API_URL}/hosts/${id}`, {
    method: 'GET'
  });
}

export async function registerHost(config: HostConfig): Promise<Host> {
  return request<Host>(`${DEPLOYMENT_API_URL}/hosts`, {
    method: 'POST',
    body: JSON.stringify(config)
  });
}

export async function updateHost(id: string, updates: Partial<HostConfig>): Promise<Host> {
  return request<Host>(`${DEPLOYMENT_API_URL}/hosts/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates)
  });
}

export async function deleteHost(id: string): Promise<{ message: string }> {
  return request<{ message: string }>(`${DEPLOYMENT_API_URL}/hosts/${id}`, {
    method: 'DELETE'
  });
}

export async function getHostMetrics(id: string): Promise<Metrics> {
  return request<Metrics>(`${DEPLOYMENT_API_URL}/hosts/${id}/metrics`, {
    method: 'GET'
  });
}

// ============================================================================
// Cost Analytics API
// ============================================================================

export async function getCostAnalytics(
  startDate?: string,
  endDate?: string
): Promise<CostData> {
  const params = new URLSearchParams();
  if (startDate) params.set('start', startDate);
  if (endDate) params.set('end', endDate);

  const queryString = params.toString();
  const url = `${DEPLOYMENT_API_URL}/analytics/costs${queryString ? `?${queryString}` : ''}`;

  return request<CostData>(url, { method: 'GET' });
}

export async function estimateDeploymentCost(req: DeployRequest): Promise<CostEstimate> {
  return request<CostEstimate>(`${DEPLOYMENT_API_URL}/estimate-cost`, {
    method: 'POST',
    body: JSON.stringify(req)
  });
}

// Alias for convenience
export const estimateCost = estimateDeploymentCost;

export async function getDeploymentCost(id: string): Promise<{
  deployment_id: string;
  total_cost: number;
  currency: string;
  breakdown: CostEstimate['breakdown'];
}> {
  return request(`${DEPLOYMENT_API_URL}/deployments/${id}/cost`, {
    method: 'GET'
  });
}

// ============================================================================
// Detection API
// ============================================================================

export async function detectAppType(files: string[]): Promise<DetectionResult> {
  return request<DetectionResult>(`${DEPLOYMENT_API_URL}/detect`, {
    method: 'POST',
    body: JSON.stringify({ files })
  });
}

export async function detectFromRepository(gitUrl: string, branch?: string): Promise<DetectionResult> {
  return request<DetectionResult>(`${DEPLOYMENT_API_URL}/detect/repository`, {
    method: 'POST',
    body: JSON.stringify({ git_url: gitUrl, branch })
  });
}

// ============================================================================
// Stats API
// ============================================================================

export async function getStats(): Promise<Stats> {
  return request<Stats>(`${DEPLOYMENT_API_URL}/stats`, {
    method: 'GET'
  });
}

export async function getProviderStats(provider: string): Promise<{
  provider: string;
  total_deployments: number;
  active_deployments: number;
  total_cost: number;
  avg_response_time: number;
}> {
  return request(`${DEPLOYMENT_API_URL}/stats/providers/${provider}`, {
    method: 'GET'
  });
}

// ============================================================================
// Health Check API
// ============================================================================

export async function healthCheck(): Promise<{ status: 'ok' | 'error'; timestamp: string }> {
  return request(`${DEPLOYMENT_API_URL}/health`, {
    method: 'GET'
  }, false); // Don't retry health checks
}

// ============================================================================
// API Client Class
// ============================================================================

export class BytePortAPI {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || DEPLOYMENT_API_URL;
  }

  // Deployments
  async deploy(req: DeployRequest): Promise<DeploymentResponse> {
    return deployApp(req);
  }

  async getDeployment(id: string): Promise<Deployment> {
    return getDeployment(id);
  }

  async getDeployments(): Promise<Deployment[]> {
    const result = await listDeployments();
    return result.deployments;
  }

  async terminate(id: string): Promise<void> {
    await terminateDeployment(id);
  }

  async restart(id: string): Promise<void> {
    await restartDeployment(id);
  }

  async updateDeployment(id: string, updates: Partial<DeployRequest>): Promise<Deployment> {
    return updateDeployment(id, updates);
  }

  // Logs
  async getLogs(id: string): Promise<LogEntry[]> {
    const result = await getDeploymentLogs(id);
    return result.logs;
  }

  streamLogs(id: string, onLog: (log: LogEntry) => void, onError?: (error: Event) => void): EventSource {
    return streamDeploymentLogs(id, onLog, onError);
  }

  streamStatus(
    id: string,
    onStatusUpdate: (status: DeploymentStatusUpdate) => void,
    onError?: (error: Event) => void
  ): EventSource {
    return streamDeploymentStatus(id, onStatusUpdate, onError);
  }

  // Metrics
  async getMetrics(id: string, query?: MetricsQuery): Promise<Metrics> {
    return getDeploymentMetrics(id, query);
  }

  streamMetrics(id: string, onMetrics: (metrics: Metrics) => void, onError?: (error: Event) => void): EventSource {
    return streamDeploymentMetrics(id, onMetrics, onError);
  }

  // Providers
  async getProviders(): Promise<Provider[]> {
    return getProviders();
  }

  async getProvider(name: string): Promise<Provider> {
    return getProvider(name);
  }

  async connectProvider(config: ProviderConfig): Promise<Provider> {
    return connectProvider(config);
  }

  async disconnectProvider(name: string): Promise<void> {
    await disconnectProvider(name);
  }

  async testProvider(name: string): Promise<boolean> {
    const result = await testProviderConnection(name);
    return result.connected;
  }

  // Hosts
  async getHosts(): Promise<Host[]> {
    return getHosts();
  }

  async getHost(id: string): Promise<Host> {
    return getHost(id);
  }

  async registerHost(config: HostConfig): Promise<Host> {
    return registerHost(config);
  }

  async deleteHost(id: string): Promise<void> {
    await deleteHost(id);
  }

  // Cost
  async getCostAnalytics(startDate?: string, endDate?: string): Promise<CostData> {
    return getCostAnalytics(startDate, endDate);
  }

  async estimateCost(req: DeployRequest): Promise<CostEstimate> {
    return estimateDeploymentCost(req);
  }

  async getDeploymentCost(id: string) {
    return getDeploymentCost(id);
  }

  // Detection
  async detectApp(files: string[]): Promise<DetectionResult> {
    return detectAppType(files);
  }

  async detectFromRepo(gitUrl: string, branch?: string): Promise<DetectionResult> {
    return detectFromRepository(gitUrl, branch);
  }

  // Stats
  async getStats(): Promise<Stats> {
    return getStats();
  }

  async getProviderStats(provider: string) {
    return getProviderStats(provider);
  }

  // Health
  async health() {
    return healthCheck();
  }
}

// Export singleton instance
export const api = new BytePortAPI();
