// Package domain contains pure domain logic with no external dependencies.
package domain

// Config is the SDK configuration.
type Config struct {
	// BaseURL is the API base URL
	BaseURL string
	// APIKey is the API key for authentication
	APIKey string
	// APIVersion is the API version to use
	APIVersion string
	// TimeoutSeconds is the request timeout in seconds
	TimeoutSeconds int
	// MaxRetries is the maximum number of retries
	MaxRetries int
	// EnableTelemetry enables telemetry
	EnableTelemetry bool
	// EnableMetrics enables metrics
	EnableMetrics bool
}

// DefaultConfig returns a configuration with sensible defaults.
func DefaultConfig() *Config {
	return &Config{
		BaseURL:          "https://api.phenotype.dev",
		APIVersion:       "v1",
		TimeoutSeconds:   30,
		MaxRetries:       3,
		EnableTelemetry:  true,
		EnableMetrics:    true,
	}
}

// Validate validates the configuration.
func (c *Config) Validate() []string {
	var errors []string

	if c.BaseURL == "" {
		errors = append(errors, "BaseURL is required")
	}

	if c.TimeoutSeconds <= 0 {
		errors = append(errors, "TimeoutSeconds must be positive")
	}

	if c.MaxRetries < 0 {
		errors = append(errors, "MaxRetries must be non-negative")
	}

	return errors
}
