// Real Forge adapter with HTTP API integration
package adapter

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/google/uuid"
)

// ForgeClient is a real HTTP client for Forge API
type ForgeClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
	Model      string
}

// ForgeConfig holds Forge API configuration
type ForgeConfig struct {
	APIKey  string
	BaseURL string
	Model   string
}

// NewForgeConfig creates Forge config from environment
func NewForgeConfig() *ForgeConfig {
	return &ForgeConfig{
		APIKey:  os.Getenv("FORGE_API_KEY"),
		BaseURL: getEnvOr("FORGE_API_URL", "https://api.forge.dev/v1"),
		Model:   getEnvOr("FORGE_MODEL", "gpt-4o"),
	}
}

// getEnvOr returns env var or default
func getEnvOr(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

// NewForgeClient creates a new Forge HTTP client
func NewForgeClient() *ForgeClient {
	cfg := NewForgeConfig()
	return &ForgeClient{
		BaseURL: cfg.BaseURL,
		APIKey:  cfg.APIKey,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		Model: cfg.Model,
	}
}

// IsConfigured checks if Forge is properly configured
func (c *ForgeClient) IsConfigured() bool {
	return c.APIKey != ""
}

// Session types for Forge API

// ForgeSession represents a session in Forge API
type ForgeSession struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name,omitempty"`
	Model         string                 `json:"model"`
	Status        string                 `json:"status"`
	CreatedAt     string                 `json:"created_at"`
	UpdatedAt     string                 `json:"updated_at"`
	Messages      []ForgeMessage         `json:"messages,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// ForgeMessage represents a message in a session
type ForgeMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ForgeCreateRequest is the request to create a session
type ForgeCreateRequest struct {
	Model    string                 `json:"model"`
	Name     string                 `json:"name,omitempty"`
	Messages []ForgeMessage         `json:"messages,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// ForgeChatRequest is a chat completion request
type ForgeChatRequest struct {
	Model       string          `json:"model"`
	Messages    []ForgeMessage  `json:"messages"`
	MaxTokens   int             `json:"max_tokens,omitempty"`
	Temperature float64         `json:"temperature,omitempty"`
	Stream      bool            `json:"stream,omitempty"`
}

// ForgeChatResponse is a chat completion response
type ForgeChatResponse struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	Model   string `json:"model"`
	Choices []struct {
		Index        int           `json:"index"`
		Message      ForgeMessage  `json:"message"`
		FinishReason string        `json:"finish_reason"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
}

// API methods

// ListSessions lists all sessions from Forge API
func (c *ForgeClient) ListSessions() ([]ForgeSession, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions"
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var sessions []ForgeSession
	if err := json.NewDecoder(resp.Body).Decode(&sessions); err != nil {
		// Read body and try wrapping in object
		body, _ := io.ReadAll(resp.Body)
		var wrapper struct {
			Sessions []ForgeSession `json:"sessions"`
			Data     []ForgeSession `json:"data"`
		}
		if err2 := json.Unmarshal(body, &wrapper); err2 == nil {
			if len(wrapper.Sessions) > 0 {
				return wrapper.Sessions, nil
			}
			if len(wrapper.Data) > 0 {
				return wrapper.Data, nil
			}
		}
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return sessions, nil
}

// CreateSession creates a new session in Forge
func (c *ForgeClient) CreateSession(req ForgeCreateRequest) (*ForgeSession, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	if req.Model == "" {
		req.Model = c.Model
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions"
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	c.setAuth(httpReq)
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var session ForgeSession
	if err := json.NewDecoder(resp.Body).Decode(&session); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return &session, nil
}

// GetSession retrieves a session by ID
func (c *ForgeClient) GetSession(sessionID string) (*ForgeSession, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions/" + sessionID
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("session not found: %s", sessionID)
	}

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var session ForgeSession
	if err := json.NewDecoder(resp.Body).Decode(&session); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return &session, nil
}

// Chat sends a chat message to a session
func (c *ForgeClient) Chat(sessionID string, messages []ForgeMessage) (*ForgeChatResponse, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions/" + sessionID + "/chat"
	chatReq := ForgeChatRequest{
		Model:    c.Model,
		Messages: messages,
	}

	body, err := json.Marshal(chatReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var chatResp ForgeChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return &chatResp, nil
}

// DeleteSession deletes a session
func (c *ForgeClient) DeleteSession(sessionID string) error {
	if !c.IsConfigured() {
		return fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions/" + sessionID
	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// TransferSession transfers session context to another harness
func (c *ForgeClient) TransferSession(sessionID string, targetHarness string) (string, error) {
	if !c.IsConfigured() {
		return "", fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	// Get current session
	session, err := c.GetSession(sessionID)
	if err != nil {
		return "", fmt.Errorf("get session: %w", err)
	}

	// Export session context
	export := map[string]interface{}{
		"source_harness": "forge",
		"target_harness": targetHarness,
		"session_id":     session.ID,
		"messages":       session.Messages,
		"model":          session.Model,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	url := c.BaseURL + "/sessions/" + sessionID + "/transfer"
	body, _ := json.Marshal(export)

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	// Return transfer token
	return fmt.Sprintf("transfer-%s-%s", sessionID, uuid.New().String()[:8]), nil
}

// setAuth sets authentication headers
func (c *ForgeClient) setAuth(req *http.Request) {
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("X-Forge-Key", c.APIKey)
}

// HealthCheck checks Forge API health
func (c *ForgeClient) HealthCheck() error {
	if !c.IsConfigured() {
		return fmt.Errorf("Forge not configured")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	url := c.BaseURL + "/health"
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return err
	}

	c.setAuth(req)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("health check failed: %d", resp.StatusCode)
	}

	return nil
}

// StreamChat streams a chat response
func (c *ForgeClient) StreamChat(sessionID string, messages []ForgeMessage) (<-chan string, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Forge not configured: FORGE_API_KEY not set")
	}

	url := c.BaseURL + "/sessions/" + sessionID + "/chat/stream"
	chatReq := ForgeChatRequest{
		Model:    c.Model,
		Messages: messages,
		Stream:   true,
	}

	body, err := json.Marshal(chatReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	c.setAuth(req)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "text/event-stream")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("do request: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	ch := make(chan string)

	go func() {
		defer close(ch)
		defer resp.Body.Close()

		// Simple SSE parsing
		dec := json.NewDecoder(resp.Body)
		for dec.More() {
			var event struct {
				Choices []struct {
					Delta struct {
						Content string `json:"content"`
					} `json:"delta"`
				} `json:"choices"`
			}
			if err := dec.Decode(&event); err != nil {
				break
			}
			if len(event.Choices) > 0 && event.Choices[0].Delta.Content != "" {
				ch <- event.Choices[0].Delta.Content
			}
		}
	}()

	return ch, nil
}
