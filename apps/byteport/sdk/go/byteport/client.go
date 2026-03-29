package byteport

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const (
	// DefaultBaseURL is the default API base URL
	DefaultBaseURL = "https://api.byteport.io/api/v1"
	// DefaultTimeout is the default HTTP timeout
	DefaultTimeout = 30 * time.Second
)

// Client is the BytePort API client
type Client struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
}

// NewClient creates a new BytePort client
func NewClient(apiKey string) *Client {
	return &Client{
		baseURL: DefaultBaseURL,
		apiKey:  apiKey,
		httpClient: &http.Client{
			Timeout: DefaultTimeout,
		},
	}
}

// WithBaseURL sets a custom base URL (for self-hosted instances)
func (c *Client) WithBaseURL(url string) *Client {
	c.baseURL = url
	return c
}

// WithHTTPClient sets a custom HTTP client
func (c *Client) WithHTTPClient(client *http.Client) *Client {
	c.httpClient = client
	return c
}

// doRequest performs an HTTP request
func (c *Client) doRequest(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewReader(jsonData)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, reqBody)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	// Execute request
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	// Check for errors
	if resp.StatusCode >= 400 {
		var errResp ErrorResponse
		if err := json.Unmarshal(respBody, &errResp); err != nil {
			return NewBytePortError(string(respBody), resp.StatusCode, "")
		}
		return NewBytePortError(errResp.Error, resp.StatusCode, errResp.Details)
	}

	// Parse response
	if result != nil && resp.StatusCode != 204 {
		if err := json.Unmarshal(respBody, result); err != nil {
			return fmt.Errorf("failed to parse response: %w", err)
		}
	}

	return nil
}

// Health checks the API health
func (c *Client) Health(ctx context.Context) (*HealthResponse, error) {
	var health HealthResponse
	if err := c.doRequest(ctx, "GET", "/health", nil, &health); err != nil {
		return nil, err
	}
	return &health, nil
}
