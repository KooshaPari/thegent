package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const flyioBaseURL = "https://api.machines.dev/v1"

// FlyioClient wraps the Fly.io Machines API.
// wraps: fly.io machines API v1 (https://fly.io/docs/machines/api/)
type FlyioClient struct {
	token      string
	httpClient *http.Client
}

// FlyApp represents a Fly.io application.
type FlyApp struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Status       string `json:"status"`
	Organization struct {
		Slug string `json:"slug"`
	} `json:"organization"`
}

// FlyMachine represents a Fly.io machine (compute instance).
type FlyMachine struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	State    string `json:"state"`
	Region   string `json:"region"`
	ImageRef struct {
		Registry   string `json:"registry"`
		Repository string `json:"repository"`
		Tag        string `json:"tag"`
	} `json:"image_ref"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

// NewFlyioClient constructs a FlyioClient with the provided token.
func NewFlyioClient(token string) *FlyioClient {
	return &FlyioClient{
		token:      token,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *FlyioClient) do(method, path string, body io.Reader) (*http.Response, error) {
	url := flyioBaseURL + path
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, fmt.Errorf("flyio: build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	return c.httpClient.Do(req)
}

// ListApps returns all Fly.io apps for the authenticated user.
func (c *FlyioClient) ListApps() ([]FlyApp, error) {
	resp, err := c.do(http.MethodGet, "/apps", nil)
	if err != nil {
		return nil, fmt.Errorf("flyio: list apps: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("flyio: list apps: unexpected status %d", resp.StatusCode)
	}
	var out []FlyApp
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("flyio: list apps: decode: %w", err)
	}
	return out, nil
}

// GetApp returns a single Fly.io app by name.
func (c *FlyioClient) GetApp(appName string) (*FlyApp, error) {
	resp, err := c.do(http.MethodGet, "/apps/"+appName, nil)
	if err != nil {
		return nil, fmt.Errorf("flyio: get app: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("flyio: get app: unexpected status %d", resp.StatusCode)
	}
	var out FlyApp
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("flyio: get app: decode: %w", err)
	}
	return &out, nil
}

// ListMachines returns all machines for a given Fly.io app name.
func (c *FlyioClient) ListMachines(appName string) ([]FlyMachine, error) {
	resp, err := c.do(http.MethodGet, "/apps/"+appName+"/machines", nil)
	if err != nil {
		return nil, fmt.Errorf("flyio: list machines: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("flyio: list machines: unexpected status %d", resp.StatusCode)
	}
	var out []FlyMachine
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("flyio: list machines: decode: %w", err)
	}
	return out, nil
}
