/**
 * BytePort type definitions
 */

export interface BytePortConfig {
  apiKey: string
  baseURL?: string
  timeout?: number
}

export interface DeployRequest {
  name: string
  type: 'frontend' | 'backend' | 'database' | 'cache'
  provider?: string
  gitUrl?: string
  branch?: string
  config?: Record<string, any>
  envVars?: Record<string, string>
}

export interface CostInfo {
  monthly: number
  currency: string
}

export interface Deployment {
  id: string
  name: string
  type: string
  status: string
  url: string
  provider: string
  gitUrl?: string
  branch?: string
  envVars?: Record<string, string>
  createdAt: string
  updatedAt: string
  message?: string
}

export interface DeploymentList {
  deployments: Deployment[]
  total: number
}

export interface DeploymentStatus {
  id: string
  status: string
  progress: number
  updatedAt: string
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
}

export interface LogsResponse {
  deployment_id: string
  logs: LogEntry[]
}

export interface Metrics {
  deployment_id: string
  uptime: string
  requests: number
  bandwidth: string
  response_time: string
  cost: CostInfo
}

export interface Project {
  id: string
  name: string
  description?: string
  deployments?: number
  createdAt: string
}

export interface ProjectList {
  projects: Project[]
}

export interface CreateProjectRequest {
  name: string
  description?: string
}

export interface DetectRequest {
  files: string[]
}

export interface DetectResponse {
  type: string
  framework: string
  confidence: number
  suggested_provider: string
}

export interface CostBreakdown {
  service: string
  provider: string
  cost: number
  plan: string
}

export interface EstimateCostRequest {
  type: string
  provider: string
}

export interface EstimateCostResponse {
  monthly: number
  currency: string
  breakdown: CostBreakdown[]
  message: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface ErrorResponse {
  error: string
  details?: string
  valid_providers?: string[]
}
