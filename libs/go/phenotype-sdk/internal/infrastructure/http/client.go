// Package infrastructure contains infrastructure implementations.
package infrastructure

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/phenotype/go-sdk/internal/application"
)

// HTTPClient is an HTTP client with retry logic.
type HTTPClient struct {
	baseURL    string
	timeout    time.Duration
	maxRetries int
	client     *http.Client
}

// Option is a functional option for HTTPClient.
type Option func(*HTTPClient)

// WithBaseURL sets the base URL.
func WithBaseURL(url string) Option {
	return func(c *HTTPClient) {
		c.baseURL = url
	}
}

// WithTimeout sets the timeout.
func WithTimeout(timeout time.Duration) Option {
	return func(c *HTTPClient) {
		c.timeout = timeout
	}
}

// WithRetry sets the maximum retries.
func WithRetry(maxRetries int) Option {
	return func(c *HTTPClient) {
		c.maxRetries = maxRetries
	}
}

// NewHTTPClient creates a new HTTP client.
func NewHTTPClient(opts ...Option) *HTTPClient {
	client := &HTTPClient{
		baseURL:    "https://api.phenotype.dev/v1",
		timeout:    30 * time.Second,
		maxRetries: 3,
	}

	for _, opt := range opts {
		opt(client)
	}

	client.client = &http.Client{
		Timeout: client.timeout,
	}

	return client
}

// Post performs a POST request with retry logic.
func (c *HTTPClient) Post(ctx context.Context, path string, req, resp interface{}, headers map[string]string) error {
	url := c.baseURL + path

	body, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "application/json")
	httpReq.Header.Set("User-Agent", "phenotype-go-sdk/0.1.0")

	for k, v := range headers {
		httpReq.Header.Set(k, v)
	}

	var lastErr error
	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			// Exponential backoff
			backoff := time.Duration(1<<uint(attempt-1)) * time.Second
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(backoff):
			}
		}

		httpResp, err := c.client.Do(httpReq)
		if err != nil {
			lastErr = err
			continue
		}
		defer httpResp.Body.Close()

		respBody, err := io.ReadAll(httpResp.Body)
		if err != nil {
			lastErr = fmt.Errorf("failed to read response: %w", err)
			continue
		}

		if httpResp.StatusCode >= 200 && httpResp.StatusCode < 300 {
			if err := json.Unmarshal(respBody, resp); err != nil {
				return fmt.Errorf("failed to unmarshal response: %w", err)
			}
			return nil
		}

		if httpResp.StatusCode == 429 {
			retryAfter := httpResp.Header.Get("Retry-After")
			return application.NewRateLimitError(retryAfter)
		}

		if httpResp.StatusCode >= 500 {
			lastErr = fmt.Errorf("server error: %d", httpResp.StatusCode)
			continue
		}

		return fmt.Errorf("client error: %d: %s", httpResp.StatusCode, string(respBody))
	}

	return lastErr
}

// Close closes the HTTP client.
func (c *HTTPClient) Close() error {
	c.client.CloseIdleConnections()
	return nil
}
