/**
 * BytePort API Client
 */

import {
  BytePortConfig,
  Deployment,
  DeployRequest,
  DeploymentList,
  DeploymentStatus,
  LogEntry,
  LogsResponse,
  Metrics,
  Project,
  ProjectList,
  CreateProjectRequest,
  DetectRequest,
  DetectResponse,
  EstimateCostRequest,
  EstimateCostResponse,
  HealthResponse,
  ErrorResponse,
} from './types'
import { BytePortError, NotFoundError, BadRequestError, ServerError } from './errors'

export class BytePortClient {
  private apiKey: string
  private baseURL: string
  private timeout: number

  constructor(config: BytePortConfig) {
    this.apiKey = config.apiKey
    this.baseURL = (config.baseURL || 'https://api.byteport.io/api/v1').replace(/\/$/, '')
    this.timeout = config.timeout || 30000
  }

  private async request<T>(
    method: string,
    path: string,
    body?: any
  ): Promise<T> {
    const url = `${this.baseURL}${path}`
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${this.apiKey}`,
    }

    if (body) {
      headers['Content-Type'] = 'application/json'
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        await this.handleError(response)
      }

      if (response.status === 204) {
        return {} as T
      }

      return await response.json()
    } catch (error) {
      clearTimeout(timeoutId)
      if (error instanceof BytePortError) {
        throw error
      }
      throw new BytePortError(
        error instanceof Error ? error.message : 'Request failed',
        0
      )
    }
  }

  private async handleError(response: Response): Promise<never> {
    let errorData: ErrorResponse
    try {
      errorData = await response.json()
    } catch {
      errorData = { error: await response.text() }
    }

    const message = errorData.error || 'Unknown error'
    const details = errorData.details || ''

    if (response.status === 404) {
      throw new NotFoundError(message, details)
    } else if (response.status === 400) {
      throw new BadRequestError(message, details)
    } else if (response.status >= 500) {
      throw new ServerError(message, details)
    } else {
      throw new BytePortError(message, response.status, details)
    }
  }

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('GET', '/health')
  }

  async deploy(request: DeployRequest): Promise<Deployment> {
    return this.request<Deployment>('POST', '/deployments', request)
  }

  async getDeployment(id: string): Promise<Deployment> {
    return this.request<Deployment>('GET', `/deployments/${id}`)
  }

  async listDeployments(): Promise<Deployment[]> {
    const data = await this.request<DeploymentList>('GET', '/deployments')
    return data.deployments
  }

  async terminate(id: string): Promise<void> {
    await this.request('DELETE', `/deployments/${id}`)
  }

  async getStatus(id: string): Promise<DeploymentStatus> {
    return this.request<DeploymentStatus>('GET', `/deployments/${id}/status`)
  }

  async getLogs(id: string, service?: string): Promise<LogEntry[]> {
    const path = service
      ? `/deployments/${id}/logs?service=${service}`
      : `/deployments/${id}/logs`
    const data = await this.request<LogsResponse>('GET', path)
    return data.logs
  }

  async *streamLogs(id: string): AsyncGenerator<LogEntry> {
    const url = `${this.baseURL}/deployments/${id}/logs?stream=true`
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Accept': 'text/event-stream',
      },
    })

    if (!response.ok) {
      await this.handleError(response)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new BytePortError('Failed to get response reader', 0)
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.trim()) {
            try {
              yield JSON.parse(line) as LogEntry
            } catch {
              // Skip invalid JSON lines
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }

  async getMetrics(id: string): Promise<Metrics> {
    return this.request<Metrics>('GET', `/deployments/${id}/metrics`)
  }

  async createProject(request: CreateProjectRequest): Promise<Project> {
    return this.request<Project>('POST', '/projects', request)
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>('GET', `/projects/${id}`)
  }

  async listProjects(): Promise<Project[]> {
    const data = await this.request<ProjectList>('GET', '/projects')
    return data.projects
  }

  async deleteProject(id: string): Promise<void> {
    await this.request('DELETE', `/projects/${id}`)
  }

  async detectAppType(files: string[]): Promise<DetectResponse> {
    return this.request<DetectResponse>('POST', '/detect', { files })
  }

  async estimateCost(type: string, provider: string): Promise<EstimateCostResponse> {
    return this.request<EstimateCostResponse>('POST', '/estimate-cost', { type, provider })
  }
}
