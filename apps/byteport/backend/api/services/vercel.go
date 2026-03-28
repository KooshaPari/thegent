package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

const vercelBaseURL = "https://api.vercel.com"

// VercelClient wraps the Vercel REST API.
// wraps: vercel REST API v1 (https://vercel.com/docs/rest-api)
type VercelClient struct {
	token      string
	httpClient *http.Client
}

// VercelProject represents a Vercel project.
type VercelProject struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	Link struct {
		Repo string `json:"repo"`
	} `json:"link"`
	Framework string `json:"framework"`
	CreatedAt int64  `json:"createdAt"`
}

// VercelDeployment represents a Vercel deployment.
type VercelDeployment struct {
	ID        string `json:"uid"`
	URL       string `json:"url"`
	Name      string `json:"name"`
	State     string `json:"readyState"`
	CreatedAt int64  `json:"createdAt"`
}

type vercelProjectsResponse struct {
	Projects []VercelProject `json:"projects"`
}

type vercelDeploymentsResponse struct {
	Deployments []VercelDeployment `json:"deployments"`
}

// NewVercelClient constructs a VercelClient with the provided token.
func NewVercelClient(token string) *VercelClient {
	return &VercelClient{
		token:      token,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *VercelClient) do(method, path string, body io.Reader) (*http.Response, error) {
	url := vercelBaseURL + path
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, fmt.Errorf("vercel: build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	return c.httpClient.Do(req)
}

// ListProjects returns all Vercel projects for the authenticated user.
func (c *VercelClient) ListProjects() ([]VercelProject, error) {
	resp, err := c.do(http.MethodGet, "/v9/projects", nil)
	if err != nil {
		return nil, fmt.Errorf("vercel: list projects: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("vercel: list projects: unexpected status %d", resp.StatusCode)
	}
	var out vercelProjectsResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("vercel: list projects: decode: %w", err)
	}
	return out.Projects, nil
}

// ListDeployments returns deployments for a given project ID.
func (c *VercelClient) ListDeployments(projectID string) ([]VercelDeployment, error) {
	path := "/v6/deployments?projectId=" + projectID
	resp, err := c.do(http.MethodGet, path, nil)
	if err != nil {
		return nil, fmt.Errorf("vercel: list deployments: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("vercel: list deployments: unexpected status %d", resp.StatusCode)
	}
	var out vercelDeploymentsResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("vercel: list deployments: decode: %w", err)
	}
	return out.Deployments, nil
}

// CreateDeployment triggers a new deployment for the given project ID.
func (c *VercelClient) CreateDeployment(projectID string) (*VercelDeployment, error) {
	payload := fmt.Sprintf(`{"name":"%s"}`, projectID)
	resp, err := c.do(http.MethodPost, "/v13/deployments", strings.NewReader(payload))
	if err != nil {
		return nil, fmt.Errorf("vercel: create deployment: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return nil, fmt.Errorf("vercel: create deployment: unexpected status %d", resp.StatusCode)
	}
	var out VercelDeployment
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("vercel: create deployment: decode: %w", err)
	}
	return &out, nil
}
