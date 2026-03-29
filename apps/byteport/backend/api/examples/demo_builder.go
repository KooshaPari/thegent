package examples

import (
	"context"
	"net/http"

	"github.com/byteport/api/internal/infrastructure/auth"
	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/byteport/api/internal/infrastructure/secrets"
	"github.com/gin-gonic/gin"
)

// WorkOSAuth abstracts the subset of WorkOS authentication behaviour used in the example router.
type WorkOSAuth interface {
	GetAuthURL(ctx context.Context, state string) (string, error)
	ExchangeCodeForToken(ctx context.Context, code string) (*auth.TokenResponse, error)
	Middleware() gin.HandlerFunc
	OptionalMiddleware() gin.HandlerFunc
}

// ExampleSecrets exposes the minimal secrets operations required by the example router.
type ExampleSecrets interface {
	WorkOSConfig(ctx context.Context) (clientID, clientSecret, apiKey string, err error)
	// LLMConfig returns the LLM base URL, model, and optional API key.
	// Supports vLLM (Linux/prod) and MLX (macOS/Apple Silicon).
	LLMConfig(ctx context.Context) (baseURL, model, apiKey string, err error)
	AWSConfig(ctx context.Context) (accessKey, secretKey, region string, err error)
}

// ExampleValidator exposes the credential validation operations used by the example router.
type ExampleValidator interface {
	ValidateAllCredentials(ctx context.Context, creds *clients.AllCredentials) []clients.CredentialValidationResult
	ListOpenAIModels(ctx context.Context, apiKey string) ([]string, error)
	ValidateAWS(ctx context.Context, accessKeyID, secretAccessKey, region string) error
}

// DemoDependencies captures the dependencies needed to build the example Gin router.
type DemoDependencies struct {
	Auth      WorkOSAuth
	Secrets   ExampleSecrets
	Validator ExampleValidator
}

// BuildExampleRouter wires the consolidated authentication routes using the supplied dependencies.
func BuildExampleRouter(ctx context.Context, deps DemoDependencies) *gin.Engine {
	router := gin.New()

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	if deps.Auth != nil {
		registerWorkOSRoutes(ctx, router, deps)
	}

	registerOptionalRoutes(router, deps.Auth)

	return router
}

func registerWorkOSRoutes(ctx context.Context, router *gin.Engine, deps DemoDependencies) {
	auth := deps.Auth

	router.GET("/auth/login", func(c *gin.Context) {
		authURL, err := auth.GetAuthURL(ctx, "random-state")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{"auth_url": authURL})
	})

	router.POST("/auth/callback", func(c *gin.Context) {
		var req struct {
			Code string `json:"code" binding:"required"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		tokens, err := auth.ExchangeCodeForToken(ctx, req.Code)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.SetCookie("authToken", tokens.AccessToken, 3600*24*7, "/", "", true, true)
		c.JSON(http.StatusOK, gin.H{"message": "Authentication successful"})
	})

	protected := router.Group("/api/v1")
	protected.Use(auth.Middleware())

	protected.GET("/me", func(c *gin.Context) {
		userInfo, ok := c.Get("user_info")
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "user context missing"})
			return
		}
		c.JSON(http.StatusOK, userInfo)
	})

	if deps.Validator != nil && deps.Secrets != nil {
		protected.POST("/validate-credentials", func(c *gin.Context) {
			var creds clients.AllCredentials
			if err := c.ShouldBindJSON(&creds); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
				return
			}

			results := deps.Validator.ValidateAllCredentials(ctx, &creds)
			c.JSON(http.StatusOK, gin.H{"results": results})
		})

		protected.GET("/llm-models", func(c *gin.Context) {
			baseURL, _, _, err := deps.Secrets.LLMConfig(ctx)
			if err != nil || baseURL == "" {
				baseURL = "http://localhost:8000" // vLLM default
			}

			models, err := deps.Validator.ListOpenAIModels(ctx, baseURL)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}

			c.JSON(http.StatusOK, gin.H{"models": models})
		})

		protected.GET("/aws-buckets", func(c *gin.Context) {
			accessKey, secretKey, region, err := deps.Secrets.AWSConfig(ctx)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "AWS not configured"})
				return
			}

			if err := deps.Validator.ValidateAWS(ctx, accessKey, secretKey, region); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}

			c.JSON(http.StatusOK, gin.H{"aws_region": region, "message": "AWS configured"})
		})
	}
}

func registerOptionalRoutes(router *gin.Engine, auth WorkOSAuth) {
	optional := router.Group("/api/public")
	if auth != nil {
		optional.Use(auth.OptionalMiddleware())
	}

	optional.GET("/stats", func(c *gin.Context) {
		userInfo, authenticated := c.Get("user_info")
		if authenticated {
			c.JSON(http.StatusOK, gin.H{
				"message": "Personalized stats",
				"user":    userInfo,
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "General stats"})
	})
}

// secretsAdapter adapts secrets.Manager to the ExampleSecrets interface.
type secretsAdapter struct {
	manager *secrets.Manager
}

func newSecretsAdapter(manager *secrets.Manager) ExampleSecrets {
	if manager == nil {
		return nil
	}
	return &secretsAdapter{manager: manager}
}

func (s *secretsAdapter) WorkOSConfig(ctx context.Context) (string, string, string, error) {
	return s.manager.GetWorkOSConfig(ctx)
}

// LLMConfig returns the LLM base URL, model, and optional API key.
// Supports vLLM (Linux/prod) and MLX (macOS/Apple Silicon).
func (s *secretsAdapter) LLMConfig(ctx context.Context) (string, string, string, error) {
	return s.manager.GetLLMConfig(ctx)
}

func (s *secretsAdapter) AWSConfig(ctx context.Context) (string, string, string, error) {
	return s.manager.GetAWSConfig(ctx)
}

// credentialValidatorAdapter adapts clients.CredentialValidator to ExampleValidator.
type credentialValidatorAdapter struct {
	validator *clients.CredentialValidator
}

func newCredentialValidatorAdapter(validator *clients.CredentialValidator) ExampleValidator {
	if validator == nil {
		return nil
	}
	return &credentialValidatorAdapter{validator: validator}
}

func (c *credentialValidatorAdapter) ValidateAllCredentials(ctx context.Context, creds *clients.AllCredentials) []clients.CredentialValidationResult {
	return c.validator.ValidateAllCredentials(ctx, creds)
}

// ListOpenAIModels probes the vLLM or MLX /v1/models endpoint and returns
// available model names. baseURL defaults to http://localhost:8000 (vLLM) when empty.
// wraps: OpenAI-compatible REST API /v1/models
func (c *credentialValidatorAdapter) ListOpenAIModels(ctx context.Context, baseURL string) ([]string, error) {
	err := c.validator.ValidateOpenAICompatCredentials(ctx, baseURL, "")
	if err != nil {
		return nil, err
	}
	// Return a static list of well-known vLLM/MLX models as a hint to callers.
	// The actual available models depend on what is loaded in the running server.
	return []string{
		"mistralai/Mistral-7B-v0.1",
		"mistralai/Mistral-7B-Instruct-v0.3",
		"mlx-community/Mistral-7B-v0.1-4bit",
		"mlx-community/Llama-3.2-3B-Instruct-4bit",
		"meta-llama/Llama-3.1-8B-Instruct",
		"Qwen/Qwen2.5-Coder-7B-Instruct",
	}, nil
}

func (c *credentialValidatorAdapter) ValidateAWS(ctx context.Context, accessKeyID, secretAccessKey, region string) error {
	return c.validator.ValidateAWSCredentials(ctx, accessKeyID, secretAccessKey, region)
}
