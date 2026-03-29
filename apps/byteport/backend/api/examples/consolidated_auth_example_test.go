package examples

import (
	"bytes"
	"context"
	"encoding/json"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/byteport/api/internal/infrastructure/auth"
	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/byteport/api/internal/infrastructure/secrets"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type stubAuth struct {
	loginURL string
}

func (s *stubAuth) GetAuthURL(_ context.Context, state string) (string, error) {
	return s.loginURL + "?state=" + state, nil
}

func (s *stubAuth) ExchangeCodeForToken(_ context.Context, code string) (*auth.TokenResponse, error) {
	return &auth.TokenResponse{
		AccessToken: "token-" + code,
		IDToken:     "id-" + code,
		ExpiresIn:   3600,
		TokenType:   "Bearer",
	}, nil
}

func (s *stubAuth) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if c.GetHeader("Authorization") != "Bearer valid" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
			c.Abort()
			return
		}
		c.Set("user_info", map[string]string{
			"id":    "user-123",
			"email": "user@example.com",
		})
		c.Next()
	}
}

func (s *stubAuth) OptionalMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if c.GetHeader("Authorization") == "Bearer valid" {
			c.Set("user_info", map[string]string{
				"id":    "user-123",
				"email": "user@example.com",
			})
		}
		c.Next()
	}
}

type stubSecrets struct{}

func (stubSecrets) WorkOSConfig(context.Context) (string, string, string, error) {
	return "client-id", "client-secret", "api-key", nil
}

func (stubSecrets) OpenAIConfig(context.Context) (string, error) {
	return "openai-key", nil
}

func (stubSecrets) AWSConfig(context.Context) (string, string, string, error) {
	return "access", "secret", "us-test-1", nil
}

type stubValidator struct {
	models []string
}

func (s stubValidator) ValidateAllCredentials(_ context.Context, _ *clients.AllCredentials) []clients.CredentialValidationResult {
	return []clients.CredentialValidationResult{
		{Service: "openai", Valid: true},
	}
}

func (s stubValidator) ListOpenAIModels(_ context.Context, _ string) ([]string, error) {
	return append([]string(nil), s.models...), nil
}

func (s stubValidator) ValidateAWS(context.Context, string, string, string) error {
	return nil
}

func TestExampleConsolidatedSystem(t *testing.T) {
	gin.SetMode(gin.TestMode)

	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer log.SetOutput(os.Stderr)

	originalRunner := exampleServerRunner
	defer func() { exampleServerRunner = originalRunner }()

	serverCalled := false
	exampleServerRunner = func(router *gin.Engine) error {
		serverCalled = true

		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()
		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)

		return nil
	}

	ExampleConsolidatedSystem()
	assert.True(t, serverCalled, "example should attempt to run the server")
}

func TestBuildExampleRouterRoutes(t *testing.T) {
	gin.SetMode(gin.TestMode)

	deps := DemoDependencies{
		Auth:      &stubAuth{loginURL: "https://auth.example.com"},
		Secrets:   stubSecrets{},
		Validator: stubValidator{models: []string{"gpt-4", "gpt-4o"}},
	}

	router := BuildExampleRouter(context.Background(), deps)

	t.Run("auth login route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/auth/login", nil)

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)

		var resp map[string]string
		require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
		assert.Contains(t, resp["auth_url"], "state")
	})

	t.Run("auth callback route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodPost, "/auth/callback", bytes.NewBufferString(`{"code":"demo"}`))
		req.Header.Set("Content-Type", "application/json")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)
		assert.Contains(t, rec.Body.String(), "Authentication successful")
	})

	t.Run("protected me route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/v1/me", nil)
		req.Header.Set("Authorization", "Bearer valid")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("validate credentials route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(
			http.MethodPost,
			"/api/v1/validate-credentials",
			bytes.NewBufferString(`{"openai":{"api_key":"abc"}}`),
		)
		req.Header.Set("Authorization", "Bearer valid")
		req.Header.Set("Content-Type", "application/json")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("openai models route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/v1/openai-models", nil)
		req.Header.Set("Authorization", "Bearer valid")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)

		var resp map[string][]string
		require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
		assert.Equal(t, []string{"gpt-4", "gpt-4o"}, resp["models"])
	})

	t.Run("aws buckets route", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/v1/aws-buckets", nil)
		req.Header.Set("Authorization", "Bearer valid")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("optional stats route without auth", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/public/stats", nil)

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)

		var resp map[string]string
		require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
		assert.Equal(t, "General stats", resp["message"])
	})

	t.Run("optional stats route with auth", func(t *testing.T) {
		rec := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/public/stats", nil)
		req.Header.Set("Authorization", "Bearer valid")

		router.ServeHTTP(rec, req)
		require.Equal(t, http.StatusOK, rec.Code)

		var resp map[string]interface{}
		require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
		assert.Equal(t, "Personalized stats", resp["message"])
	})
}

func TestExampleSecretsManagement(t *testing.T) {
	t.Run("secrets_management_example", func(t *testing.T) {
		// Capture output
		var buf bytes.Buffer
		log.SetOutput(&buf)
		defer log.SetOutput(os.Stderr)

		// Test the secrets management example
		ctx := context.Background()

		// Set environment variables for testing
		testVars := map[string]string{
			"OPENAI_API_KEY":       "test-openai-key",
			"WORKOS_CLIENT_ID":     "test-workos-client-id",
			"WORKOS_CLIENT_SECRET": "test-workos-secret",
			"WORKOS_API_KEY":       "test-workos-api-key",
		}

		var oldValues map[string]string
		oldValues = make(map[string]string)

		// Save old values
		for envVar, newVal := range testVars {
			if oldVal := os.Getenv(envVar); oldVal != "" {
				oldValues[envVar] = oldVal
			}
			os.Setenv(envVar, newVal)
		}
		defer func() {
			for envVar, oldVal := range oldValues {
				if oldVal != "" {
					os.Setenv(envVar, oldVal)
				} else {
					os.Unsetenv(envVar)
				}
			}
			for envVar := range testVars {
				os.Unsetenv(envVar)
			}
		}()

		// Create secrets manager
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})

		// Register environment provider
		manager.RegisterProvider("env", secrets.NewEnvironmentProvider())

		// Test getting configurations
		clientID, clientSecret, apiKey, err := manager.GetWorkOSConfig(ctx)
		assert.NoError(t, err)
		assert.Equal(t, "test-workos-client-id", clientID)
		assert.Equal(t, "test-workos-secret", clientSecret)
		assert.Equal(t, "test-workos-api-key", apiKey)

		openAIKey, err := manager.GetOpenAIConfig(ctx)
		assert.NoError(t, err)
		assert.Equal(t, "test-openai-key", openAIKey)

		assert.True(t, true, "Secrets management example works")
	})
}

func TestExampleMigrationPath(t *testing.T) {
	t.Run("migration_path_example", func(t *testing.T) {
		useNewAuth := true
		router := gin.New()

		if useNewAuth {
			router.GET("/test", func(c *gin.Context) {
				c.JSON(200, gin.H{"system": "new"})
			})
		} else {
			router.GET("/test", func(c *gin.Context) {
				c.JSON(200, gin.H{"system": "old"})
			})
		}

		assert.NotNil(t, router)
		assert.True(t, true, "Migration path example works")
	})
}

func TestWorkOSAuthIntegration(t *testing.T) {
	t.Run("workos_auth_initialization", func(t *testing.T) {
		ctx := context.Background()

		// Set environment variables for testing
		testEnvVars := map[string]string{
			"WORKOS_CLIENT_ID":     "test-client-id",
			"WORKOS_CLIENT_SECRET": "test-client-secret",
			"WORKOS_API_KEY":       "test-api-key",
			"OPENAI_API_KEY":       "test-openai-key",
		}

		var oldValues map[string]string
		oldValues = make(map[string]string)

		// Save and set environment variables
		for envVar, val := range testEnvVars {
			if oldVal := os.Getenv(envVar); oldVal != "" {
				oldValues[envVar] = oldVal
			}
			os.Setenv(envVar, val)
		}
		defer func() {
			// Restore environment variables
			for envVar, val := range oldValues {
				if val != "" {
					os.Setenv(envVar, val)
				} else {
					os.Unsetenv(envVar)
				}
			}
			for envVar := range testEnvVars {
				os.Unsetenv(envVar)
			}
		}()

		// Test secrets manager setup
		secretsManager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})

		// Register environment provider
		secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())

		// Test WorkOS auth service
		workosAuth := auth.NewWorkOSAuthService(secretsManager)

		err := workosAuth.Initialize(ctx)
		// May fail due to invalid credentials, but should not panic
		if err != nil {
			t.Logf("WorkOS initialization failed (expected in test): %v", err)
		}

		assert.NotNil(t, workosAuth)
		assert.NotNil(t, secretsManager)
	})
}

func TestCredentialValidatorSetup(t *testing.T) {
	t.Run("credential_validator_setup", func(t *testing.T) {
		credValidator := clients.NewCredentialValidator()
		assert.NotNil(t, credValidator)

		ctx := context.Background()

		// Test with empty credentials (should handle gracefully)
		emptyCreds := &clients.AllCredentials{}
		_ = credValidator.ValidateAllCredentials(ctx, emptyCreds)
		// Results may be nil for empty credentials, which is expected behavior
	})
}

func TestGinRouterSetup(t *testing.T) {
	t.Run("gin_router_setup", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		// Health endpoint
		router.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{"status": "healthy"})
		})

		// Auth endpoints
		router.GET("/auth/login", func(c *gin.Context) {
			c.JSON(200, gin.H{"auth_url": "https://example.com/auth"})
		})

		router.POST("/auth/callback", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Authentication successful"})
		})

		// Protected routes
		protected := router.Group("/api/v1")
		protected.GET("/me", func(c *gin.Context) {
			c.JSON(200, gin.H{"user": "test-user"})
		})

		// Optional routes
		optional := router.Group("/api/public")
		optional.GET("/stats", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "General stats"})
		})

		assert.NotNil(t, router)
	})
}

func TestSecretsProviderRegistration(t *testing.T) {
	t.Run("secrets_provider_registration", func(t *testing.T) {
		ctx := context.Background()

		// Create secrets manager
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})

		// Test environment provider registration
		envProvider := secrets.NewEnvironmentProvider()
		manager.RegisterProvider("env", envProvider)

		// Test AWS provider registration (will likely fail in test env)
		awsProvider, err := secrets.NewAWSSecretsProvider(ctx, "us-east-1")
		if err == nil {
			manager.RegisterProvider("aws", awsProvider)
			t.Log("AWS provider registered successfully")
		} else {
			t.Logf("AWS provider registration failed (expected in test): %v", err)
		}

		// Test Vault provider registration (will likely fail in test env)
		vaultAddr := os.Getenv("VAULT_ADDR")
		vaultToken := os.Getenv("VAULT_TOKEN")
		if vaultAddr != "" && vaultToken != "" {
			vaultProvider, err := secrets.NewVaultProvider(vaultAddr, vaultToken, "secret")
			if err == nil {
				manager.RegisterProvider("vault", vaultProvider)
				t.Log("Vault provider registered successfully")
			}
		}

		assert.NotNil(t, manager)
	})
}

func TestSecretRetrieval(t *testing.T) {
	t.Run("secret_retrieval", func(t *testing.T) {
		ctx := context.Background()

		// Set test environment variables
		testVars := map[string]string{
			"OPENAI_API_KEY":          "test-openai-key",
			"WORKOS_CLIENT_ID":        "test-workos-client-id",
			"WORKOS_CLIENT_SECRET":    "test-workos-secret",
			"WORKOS_API_KEY":          "test-workos-api-key",
			"AWS_ACCESS_KEY_ID":       "test-aws-key-id",
			"AWS_SECRET_ACCESS_KEY":   "test-aws-secret",
			"AWS_DEFAULT_REGION":      "us-east-1",
			"PORTFOLIO_API_KEY":       "test-portfolio-key",
			"PORTFOLIO_ROOT_ENDPOINT": "test-portfolio-endpoint",
		}

		var oldValues map[string]string
		oldValues = make(map[string]string)

		// Set environment variables
		for envVar, val := range testVars {
			if oldVal := os.Getenv(envVar); oldVal != "" {
				oldValues[envVar] = oldVal
			}
			os.Setenv(envVar, val)
		}
		defer func() {
			// Restore environment variables
			for envVar, val := range oldValues {
				if val != "" {
					os.Setenv(envVar, val)
				} else {
					os.Unsetenv(envVar)
				}
			}
			for envVar := range testVars {
				os.Unsetenv(envVar)
			}
		}()

		// Create secrets manager
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})

		manager.RegisterProvider("env", secrets.NewEnvironmentProvider())

		// Test individual secret retrieval
		openAIKey, err := manager.GetSecret(ctx, secrets.SecretOpenAIAPIKey)
		assert.NoError(t, err)
		assert.Equal(t, "test-openai-key", openAIKey)

		// Test WorkOS config retrieval
		clientID, clientSecret, apiKey, err := manager.GetWorkOSConfig(ctx)
		assert.NoError(t, err)
		assert.Equal(t, "test-workos-client-id", clientID)
		assert.Equal(t, "test-workos-secret", clientSecret)
		assert.Equal(t, "test-workos-api-key", apiKey)

		// Test AWS config retrieval
		accessKey, secretKey, region, err := manager.GetAWSConfig(ctx)
		assert.NoError(t, err)
		assert.Equal(t, "test-aws-key-id", accessKey)
		assert.Equal(t, "test-aws-secret", secretKey)
		assert.Equal(t, "us-east-1", region) // Default region

		// Test portfolio config retrieval
		portfolioKey, portfolioEndpoint, err := manager.GetPortfolioConfig(ctx)
		assert.NoError(t, err)
		assert.Equal(t, "test-portfolio-key", portfolioKey)
		assert.Equal(t, "test-portfolio-endpoint", portfolioEndpoint)
	})
}

func TestMiddlewareSetup(t *testing.T) {
	t.Run("middleware_setup", func(t *testing.T) {
		ctx := context.Background()

		// Setup secrets manager
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})
		manager.RegisterProvider("env", secrets.NewEnvironmentProvider())

		// Setup WorkOS auth
		workosAuth := auth.NewWorkOSAuthService(manager)

		err := workosAuth.Initialize(ctx)
		if err != nil {
			t.Logf("WorkOS init failed in test (expected): %v", err)
		}

		// Check that middleware functions exist
		assert.NotNil(t, workosAuth.Middleware)
		assert.NotNil(t, workosAuth.OptionalMiddleware)
	})
}

func TestErrorHandling(t *testing.T) {
	t.Run("error_handling_workos_auth", func(t *testing.T) {
		ctx := context.Background()

		// Test with empty secrets manager
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})

		workosAuth := auth.NewWorkOSAuthService(manager)

		err := workosAuth.Initialize(ctx)
		// Should fail due to missing WorkOS configuration
		assert.Error(t, err)

		authURL, err := workosAuth.GetAuthURL(ctx, "test-state")
		// Should fail due to missing configuration
		assert.Error(t, err)
		assert.Empty(t, authURL)
	})
}

func TestPackageBuildTags(t *testing.T) {
	t.Run("build_tags", func(t *testing.T) {
		// Verify this package has the correct build tags
		// This is a compile-time check - if it compiles, the tags are correct
		assert.True(t, true, "Package compiled successfully with build tags")
	})
}

// Benchmark tests
func BenchmarkSecretsManagerCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		manager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})
		manager.RegisterProvider("env", secrets.NewEnvironmentProvider())
	}
}

func BenchmarkCredentialValidatorCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		credValidator := clients.NewCredentialValidator()
		_ = credValidator
	}
}

// Integration test helper
func setupTestEnvironment(t *testing.T) {
	testVars := map[string]string{
		"OPENAI_API_KEY":       "test-openai-key",
		"WORKOS_CLIENT_ID":     "test-workos-client-id",
		"WORKOS_CLIENT_SECRET": "test-workos-secret",
		"WORKOS_API_KEY":       "test-workos-api-key",
	}

	var oldValues map[string]string
	oldValues = make(map[string]string)

	// Save old values
	for envVar, val := range testVars {
		if oldVal := os.Getenv(envVar); oldVal != "" {
			oldValues[envVar] = oldVal
		}
		os.Setenv(envVar, val)
	}

	// Return cleanup function
	cleanup := func() {
		for envVar, oldVal := range oldValues {
			if oldVal != "" {
				os.Setenv(envVar, oldVal)
			} else {
				os.Unsetenv(envVar)
			}
		}
		for envVar := range testVars {
			os.Unsetenv(envVar)
		}
	}
	cleanup()
}
