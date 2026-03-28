// Package sdk provides the Phenotype Go SDK.
//
// Following hexagonal architecture principles:
// - Domain layer: Pure business logic with no external dependencies
// - Application layer: Use cases and services
// - Infrastructure layer: External integrations (HTTP, retry, etc.)
//
// Usage:
//
//	config := sdk.NewConfig()
//	config.APIKey = "your-api-key"
//
//	client := sdk.NewClient(config)
//	resp, err := client.Query(ctx, "hello", nil)
package sdk

import (
	"context"
	"net/http"
	"time"

	"github.com/phenotype/go-sdk/internal/application"
	"github.com/phenotype/go-sdk/internal/domain"
	"github.com/phenotype/go-sdk/internal/infrastructure"
)

// Client is the main SDK client.
type Client struct {
	config     *domain.Config
	httpClient *infrastructure.HTTPClient
	auth       *application.AuthService
}

// NewClient creates a new SDK client.
func NewClient(config *domain.Config) *Client {
	httpClient := infrastructure.NewHTTPClient(
		infrastructure.WithBaseURL(config.BaseURL),
		infrastructure.WithTimeout(time.Duration(config.TimeoutSeconds)*time.Second),
		infrastructure.WithRetry(config.MaxRetries),
	)

	authService := application.NewAuthService(config)

	return &Client{
		config:     config,
		httpClient: httpClient,
		auth:       authService,
	}
}

// Query sends a query to the API.
func (c *Client) Query(ctx context.Context, prompt string, variables map[string]interface{}) (*domain.QueryResponse, error) {
	headers := c.auth.GetHeaders()

	var req domain.QueryRequest
	req.Prompt = prompt
	req.Variables = variables

	var resp domain.QueryResponse
	err := c.httpClient.Post(ctx, "/query", req, &resp, headers)
	if err != nil {
		return nil, err
	}

	return &resp, nil
}

// Execute sends an execution request to the API.
func (c *Client) Execute(ctx context.Context, task string, context map[string]interface{}) (*domain.ExecuteResponse, error) {
	headers := c.auth.GetHeaders()

	var req domain.ExecuteRequest
	req.Task = task
	req.Context = context

	var resp domain.ExecuteResponse
	err := c.httpClient.Post(ctx, "/execute", req, &resp, headers)
	if err != nil {
		return nil, err
	}

	return &resp, nil
}

// Close closes the client and releases resources.
func (c *Client) Close() error {
	return c.httpClient.Close()
}
