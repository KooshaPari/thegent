package byteport

import "time"

// DeployRequest represents a deployment request
type DeployRequest struct {
	Name     string            `json:"name"`
	Type     string            `json:"type"` // frontend, backend, database, cache
	Provider string            `json:"provider,omitempty"`
	GitURL   string            `json:"git_url,omitempty"`
	Branch   string            `json:"branch,omitempty"`
	Config   map[string]interface{} `json:"config,omitempty"`
	EnvVars  map[string]string `json:"env_vars,omitempty"`
}

// Deployment represents a deployment response
type Deployment struct {
	ID        string            `json:"id"`
	Name      string            `json:"name"`
	Type      string            `json:"type"`
	Status    string            `json:"status"`
	URL       string            `json:"url"`
	Provider  string            `json:"provider"`
	GitURL    string            `json:"git_url,omitempty"`
	Branch    string            `json:"branch,omitempty"`
	EnvVars   map[string]string `json:"env_vars,omitempty"`
	CreatedAt time.Time         `json:"created_at"`
	UpdatedAt time.Time         `json:"updated_at"`
	Message   string            `json:"message,omitempty"`
}

// DeploymentList represents a list of deployments
type DeploymentList struct {
	Deployments []Deployment `json:"deployments"`
	Total       int          `json:"total"`
}

// DeploymentStatus represents deployment status
type DeploymentStatus struct {
	ID        string    `json:"id"`
	Status    string    `json:"status"`
	Progress  int       `json:"progress"`
	UpdatedAt time.Time `json:"updated_at"`
}

// LogEntry represents a deployment log entry
type LogEntry struct {
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
}

// LogsResponse represents logs response
type LogsResponse struct {
	DeploymentID string     `json:"deployment_id"`
	Logs         []LogEntry `json:"logs"`
}

// Metrics represents deployment metrics
type Metrics struct {
	DeploymentID string   `json:"deployment_id"`
	Uptime       string   `json:"uptime"`
	Requests     int      `json:"requests"`
	Bandwidth    string   `json:"bandwidth"`
	ResponseTime string   `json:"response_time"`
	Cost         CostInfo `json:"cost"`
}

// CostInfo represents cost information
type CostInfo struct {
	Monthly  float64 `json:"monthly"`
	Currency string  `json:"currency"`
}

// Project represents a project
type Project struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description,omitempty"`
	Deployments int       `json:"deployments,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

// ProjectList represents a list of projects
type ProjectList struct {
	Projects []Project `json:"projects"`
}

// CreateProjectRequest represents a project creation request
type CreateProjectRequest struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
}

// DetectRequest represents an app type detection request
type DetectRequest struct {
	Files []string `json:"files"`
}

// DetectResponse represents app type detection response
type DetectResponse struct {
	Type              string  `json:"type"`
	Framework         string  `json:"framework"`
	Confidence        float64 `json:"confidence"`
	SuggestedProvider string  `json:"suggested_provider"`
}

// EstimateCostRequest represents a cost estimation request
type EstimateCostRequest struct {
	Type     string `json:"type"`
	Provider string `json:"provider"`
}

// CostBreakdown represents cost breakdown for a service
type CostBreakdown struct {
	Service  string  `json:"service"`
	Provider string  `json:"provider"`
	Cost     float64 `json:"cost"`
	Plan     string  `json:"plan"`
}

// EstimateCostResponse represents cost estimation response
type EstimateCostResponse struct {
	Monthly   float64         `json:"monthly"`
	Currency  string          `json:"currency"`
	Breakdown []CostBreakdown `json:"breakdown"`
	Message   string          `json:"message"`
}

// HealthResponse represents health check response
type HealthResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
}

// ErrorResponse represents an API error
type ErrorResponse struct {
	Error   string   `json:"error"`
	Details string   `json:"details,omitempty"`
	Valid   []string `json:"valid_providers,omitempty"`
}

// LogOptions represents options for log retrieval
type LogOptions struct {
	Service string
	Since   time.Time
	Tail    int
}
