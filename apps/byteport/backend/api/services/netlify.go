package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const netlifyBaseURL = "https://api.netlify.com/api/v1"

// NetlifyClient wraps the Netlify REST API.
// wraps: netlify REST API v1 (https://docs.netlify.com/api/get-started/)
type NetlifyClient struct {
	token      string
	httpClient *http.Client
}

// NetlifySite represents a Netlify site.
type NetlifySite struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	URL          string `json:"url"`
	AdminURL     string `json:"admin_url"`
	DeployURL    string `json:"deploy_url"`
	State        string `json:"state"`
	CreatedAt    string `json:"created_at"`
	UpdatedAt    string `json:"updated_at"`
	CustomDomain string `json:"custom_domain"`
}

// NetlifyDeploy represents a Netlify deploy.
type NetlifyDeploy struct {
	ID        string `json:"id"`
	SiteID    string `json:"site_id"`
	URL       string `json:"deploy_url"`
	State     string `json:"state"`
	Branch    string `json:"branch"`
	CommitRef string `json:"commit_ref"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

// NewNetlifyClient constructs a NetlifyClient with the provided token.
func NewNetlifyClient(token string) *NetlifyClient {
	return &NetlifyClient{
		token:      token,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *NetlifyClient) do(method, path string, body io.Reader) (*http.Response, error) {
	url := netlifyBaseURL + path
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, fmt.Errorf("netlify: build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	return c.httpClient.Do(req)
}

// ListSites returns all Netlify sites for the authenticated user.
func (c *NetlifyClient) ListSites() ([]NetlifySite, error) {
	resp, err := c.do(http.MethodGet, "/sites", nil)
	if err != nil {
		return nil, fmt.Errorf("netlify: list sites: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("netlify: list sites: unexpected status %d", resp.StatusCode)
	}
	var out []NetlifySite
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("netlify: list sites: decode: %w", err)
	}
	return out, nil
}

// GetSite returns a single Netlify site by ID.
func (c *NetlifyClient) GetSite(siteID string) (*NetlifySite, error) {
	resp, err := c.do(http.MethodGet, "/sites/"+siteID, nil)
	if err != nil {
		return nil, fmt.Errorf("netlify: get site: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("netlify: get site: unexpected status %d", resp.StatusCode)
	}
	var out NetlifySite
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("netlify: get site: decode: %w", err)
	}
	return &out, nil
}

// ListDeploys returns all deploys for a given site ID.
func (c *NetlifyClient) ListDeploys(siteID string) ([]NetlifyDeploy, error) {
	resp, err := c.do(http.MethodGet, "/sites/"+siteID+"/deploys", nil)
	if err != nil {
		return nil, fmt.Errorf("netlify: list deploys: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("netlify: list deploys: unexpected status %d", resp.StatusCode)
	}
	var out []NetlifyDeploy
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("netlify: list deploys: decode: %w", err)
	}
	return out, nil
}
