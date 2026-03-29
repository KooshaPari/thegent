package byteport

import "context"

// CreateProject creates a new project
func (c *Client) CreateProject(ctx context.Context, req *CreateProjectRequest) (*Project, error) {
	var project Project
	if err := c.doRequest(ctx, "POST", "/projects", req, &project); err != nil {
		return nil, err
	}
	return &project, nil
}

// GetProject retrieves a project by ID
func (c *Client) GetProject(ctx context.Context, id string) (*Project, error) {
	var project Project
	if err := c.doRequest(ctx, "GET", "/projects/"+id, nil, &project); err != nil {
		return nil, err
	}
	return &project, nil
}

// ListProjects lists all projects
func (c *Client) ListProjects(ctx context.Context) (*ProjectList, error) {
	var list ProjectList
	if err := c.doRequest(ctx, "GET", "/projects", nil, &list); err != nil {
		return nil, err
	}
	return &list, nil
}

// DeleteProject deletes a project
func (c *Client) DeleteProject(ctx context.Context, id string) error {
	var response map[string]interface{}
	return c.doRequest(ctx, "DELETE", "/projects/"+id, nil, &response)
}
