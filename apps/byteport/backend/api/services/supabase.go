package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const supabaseBaseURL = "https://api.supabase.com/v1"

// SupabaseClient wraps the Supabase Management API.
// wraps: supabase management API v1 (https://supabase.com/docs/reference/api)
type SupabaseClient struct {
	token      string
	httpClient *http.Client
}

// SupabaseProject represents a Supabase project.
type SupabaseProject struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Status       string `json:"status"`
	Region       string `json:"region"`
	OrganizationID string `json:"organization_id"`
	CreatedAt    string `json:"created_at"`
}

// NewSupabaseClient constructs a SupabaseClient with the provided token.
func NewSupabaseClient(token string) *SupabaseClient {
	return &SupabaseClient{
		token:      token,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *SupabaseClient) do(method, path string, body io.Reader) (*http.Response, error) {
	url := supabaseBaseURL + path
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, fmt.Errorf("supabase: build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	return c.httpClient.Do(req)
}

// ListProjects returns all Supabase projects for the authenticated user.
func (c *SupabaseClient) ListProjects() ([]SupabaseProject, error) {
	resp, err := c.do(http.MethodGet, "/projects", nil)
	if err != nil {
		return nil, fmt.Errorf("supabase: list projects: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("supabase: list projects: unexpected status %d", resp.StatusCode)
	}
	var out []SupabaseProject
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("supabase: list projects: decode: %w", err)
	}
	return out, nil
}

// GetProject returns a single Supabase project by ID.
func (c *SupabaseClient) GetProject(id string) (*SupabaseProject, error) {
	resp, err := c.do(http.MethodGet, "/projects/"+id, nil)
	if err != nil {
		return nil, fmt.Errorf("supabase: get project: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("supabase: get project: unexpected status %d", resp.StatusCode)
	}
	var out SupabaseProject
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("supabase: get project: decode: %w", err)
	}
	return &out, nil
}
