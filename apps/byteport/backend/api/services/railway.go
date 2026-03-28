package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const railwayGraphQLURL = "https://backboard.railway.app/graphql/v2"

// RailwayClient wraps the Railway GraphQL API.
// wraps: railway graphql v2 (https://docs.railway.app/reference/public-api)
type RailwayClient struct {
	token      string
	httpClient *http.Client
}

// RailwayProject represents a Railway project.
type RailwayProject struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	CreatedAt   string `json:"createdAt"`
	UpdatedAt   string `json:"updatedAt"`
}

type railwayGQLRequest struct {
	Query     string                 `json:"query"`
	Variables map[string]interface{} `json:"variables,omitempty"`
}

type railwayProjectsResponse struct {
	Data struct {
		Projects struct {
			Edges []struct {
				Node RailwayProject `json:"node"`
			} `json:"edges"`
		} `json:"projects"`
	} `json:"data"`
	Errors []struct {
		Message string `json:"message"`
	} `json:"errors"`
}

type railwayProjectResponse struct {
	Data struct {
		Project RailwayProject `json:"project"`
	} `json:"data"`
	Errors []struct {
		Message string `json:"message"`
	} `json:"errors"`
}

type railwayDeployResponse struct {
	Data struct {
		ServiceInstanceDeploy bool `json:"serviceInstanceDeploy"`
	} `json:"data"`
	Errors []struct {
		Message string `json:"message"`
	} `json:"errors"`
}

// NewRailwayClient constructs a RailwayClient with the provided token.
func NewRailwayClient(token string) *RailwayClient {
	return &RailwayClient{
		token:      token,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *RailwayClient) gql(query string, variables map[string]interface{}, out interface{}) error {
	payload := railwayGQLRequest{Query: query, Variables: variables}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("railway: marshal request: %w", err)
	}
	req, err := http.NewRequest(http.MethodPost, railwayGraphQLURL, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("railway: build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("railway: execute request: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("railway: unexpected status %d", resp.StatusCode)
	}
	if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
		return fmt.Errorf("railway: decode response: %w", err)
	}
	return nil
}

// ListProjects returns all Railway projects for the authenticated user.
func (c *RailwayClient) ListProjects() ([]RailwayProject, error) {
	query := `query { projects { edges { node { id name description createdAt updatedAt } } } }`
	var result railwayProjectsResponse
	if err := c.gql(query, nil, &result); err != nil {
		return nil, fmt.Errorf("railway: list projects: %w", err)
	}
	if len(result.Errors) > 0 {
		return nil, fmt.Errorf("railway: list projects: %s", result.Errors[0].Message)
	}
	projects := make([]RailwayProject, 0, len(result.Data.Projects.Edges))
	for _, edge := range result.Data.Projects.Edges {
		projects = append(projects, edge.Node)
	}
	return projects, nil
}

// GetProject returns a single Railway project by ID.
func (c *RailwayClient) GetProject(id string) (*RailwayProject, error) {
	query := `query($id: String!) { project(id: $id) { id name description createdAt updatedAt } }`
	var result railwayProjectResponse
	if err := c.gql(query, map[string]interface{}{"id": id}, &result); err != nil {
		return nil, fmt.Errorf("railway: get project: %w", err)
	}
	if len(result.Errors) > 0 {
		return nil, fmt.Errorf("railway: get project: %s", result.Errors[0].Message)
	}
	return &result.Data.Project, nil
}

// TriggerDeploy triggers a deployment for the given serviceId and environmentId.
func (c *RailwayClient) TriggerDeploy(serviceID, environmentID string) error {
	mutation := `mutation($serviceId: String!, $environmentId: String!) {
		serviceInstanceDeploy(serviceId: $serviceId, environmentId: $environmentId)
	}`
	var result railwayDeployResponse
	vars := map[string]interface{}{
		"serviceId":     serviceID,
		"environmentId": environmentID,
	}
	if err := c.gql(mutation, vars, &result); err != nil {
		return fmt.Errorf("railway: trigger deploy: %w", err)
	}
	if len(result.Errors) > 0 {
		return fmt.Errorf("railway: trigger deploy: %s", result.Errors[0].Message)
	}
	return nil
}
