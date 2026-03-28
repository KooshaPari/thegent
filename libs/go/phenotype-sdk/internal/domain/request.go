package domain

// QueryRequest is a query request.
type QueryRequest struct {
	Prompt    string                 `json:"prompt"`
	Variables map[string]interface{} `json:"variables,omitempty"`
}

// QueryResponse is a query response.
type QueryResponse struct {
	Data   map[string]interface{} `json:"data,omitempty"`
	Errors []QueryError          `json:"errors,omitempty"`
}

// QueryError is a query error.
type QueryError struct {
	Message string `json:"message"`
	Code    string `json:"code,omitempty"`
}

// ExecuteRequest is an execution request.
type ExecuteRequest struct {
	Task    string                 `json:"task"`
	Context map[string]interface{} `json:"context,omitempty"`
}

// ExecuteResponse is an execution response.
type ExecuteResponse struct {
	Result map[string]interface{} `json:"result,omitempty"`
	Errors []QueryError         `json:"errors,omitempty"`
	Status string               `json:"status,omitempty"`
}
