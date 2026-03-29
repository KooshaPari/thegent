package byteport

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"net/url"
)

// Deploy creates a new deployment
func (c *Client) Deploy(ctx context.Context, req *DeployRequest) (*Deployment, error) {
	var deployment Deployment
	if err := c.doRequest(ctx, "POST", "/deployments", req, &deployment); err != nil {
		return nil, err
	}
	return &deployment, nil
}

// GetDeployment retrieves a deployment by ID
func (c *Client) GetDeployment(ctx context.Context, id string) (*Deployment, error) {
	var deployment Deployment
	if err := c.doRequest(ctx, "GET", "/deployments/"+id, nil, &deployment); err != nil {
		return nil, err
	}
	return &deployment, nil
}

// ListDeployments lists all deployments
func (c *Client) ListDeployments(ctx context.Context) (*DeploymentList, error) {
	var list DeploymentList
	if err := c.doRequest(ctx, "GET", "/deployments", nil, &list); err != nil {
		return nil, err
	}
	return &list, nil
}

// Terminate terminates a deployment
func (c *Client) Terminate(ctx context.Context, id string) error {
	var response map[string]interface{}
	return c.doRequest(ctx, "DELETE", "/deployments/"+id, nil, &response)
}

// GetStatus retrieves deployment status
func (c *Client) GetStatus(ctx context.Context, id string) (*DeploymentStatus, error) {
	var status DeploymentStatus
	if err := c.doRequest(ctx, "GET", "/deployments/"+id+"/status", nil, &status); err != nil {
		return nil, err
	}
	return &status, nil
}

// GetLogs retrieves deployment logs
func (c *Client) GetLogs(ctx context.Context, id string, opts *LogOptions) (*LogsResponse, error) {
	path := "/deployments/" + id + "/logs"

	// Add query parameters if provided
	if opts != nil {
		params := url.Values{}
		if opts.Service != "" {
			params.Add("service", opts.Service)
		}
		if !opts.Since.IsZero() {
			params.Add("since", opts.Since.Format("2006-01-02T15:04:05Z"))
		}
		if opts.Tail > 0 {
			params.Add("tail", fmt.Sprintf("%d", opts.Tail))
		}
		if len(params) > 0 {
			path += "?" + params.Encode()
		}
	}

	var logs LogsResponse
	if err := c.doRequest(ctx, "GET", path, nil, &logs); err != nil {
		return nil, err
	}
	return &logs, nil
}

// StreamLogs streams deployment logs in real-time
func (c *Client) StreamLogs(ctx context.Context, id string) (<-chan LogEntry, <-chan error, error) {
	logChan := make(chan LogEntry, 100)
	errChan := make(chan error, 1)

	req, err := c.createStreamRequest(ctx, "/deployments/"+id+"/logs?stream=true")
	if err != nil {
		return nil, nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, nil, fmt.Errorf("stream request failed: %w", err)
	}

	if resp.StatusCode != 200 {
		defer resp.Body.Close()
		var errResp ErrorResponse
		if err := json.NewDecoder(resp.Body).Decode(&errResp); err != nil {
			return nil, nil, NewBytePortError("stream failed", resp.StatusCode, "")
		}
		return nil, nil, NewBytePortError(errResp.Error, resp.StatusCode, errResp.Details)
	}

	go func() {
		defer resp.Body.Close()
		defer close(logChan)
		defer close(errChan)

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			select {
			case <-ctx.Done():
				errChan <- ctx.Err()
				return
			default:
				line := scanner.Text()
				if line == "" {
					continue
				}

				var logEntry LogEntry
				if err := json.Unmarshal([]byte(line), &logEntry); err != nil {
					errChan <- fmt.Errorf("failed to parse log entry: %w", err)
					return
				}

				select {
				case logChan <- logEntry:
				case <-ctx.Done():
					errChan <- ctx.Err()
					return
				}
			}
		}

		if err := scanner.Err(); err != nil {
			errChan <- fmt.Errorf("stream error: %w", err)
		}
	}()

	return logChan, errChan, nil
}

// GetMetrics retrieves deployment metrics
func (c *Client) GetMetrics(ctx context.Context, id string) (*Metrics, error) {
	var metrics Metrics
	if err := c.doRequest(ctx, "GET", "/deployments/"+id+"/metrics", nil, &metrics); err != nil {
		return nil, err
	}
	return &metrics, nil
}

// createStreamRequest creates an HTTP request for streaming
func (c *Client) createStreamRequest(ctx context.Context, path string) (*http.Request, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+path, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create stream request: %w", err)
	}

	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}
	req.Header.Set("Accept", "text/event-stream")

	return req, nil
}

// WaitForDeployment waits for a deployment to complete
func (c *Client) WaitForDeployment(ctx context.Context, id string) (*Deployment, error) {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-ticker.C:
			status, err := c.GetStatus(ctx, id)
			if err != nil {
				return nil, err
			}

			if status.Status == "deployed" || status.Status == "failed" || status.Status == "terminated" {
				return c.GetDeployment(ctx, id)
			}
		}
	}
}
