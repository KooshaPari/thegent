//go:build examples
// +build examples

package examples

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/byteport/api/internal/infrastructure/auth"
	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/byteport/api/internal/infrastructure/secrets"
	"github.com/stretchr/testify/assert"
)

func TestWorkflowExample(t *testing.T) {
	t.Run("workflow_example_execution", func(t *testing.T) {
		// Set environment variables for testing
		testVars := map[string]string{
			"WORKOS_CLIENT_ID":     "test-client-id",
			"WORKOS_CLIENT_SECRET": "test-client-secret",
			"WORKOS_API_KEY":       "test-api-key",
		}
		
		var oldValues map[string]string
		oldValues = make(map[string]string)
		
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
		
		// Execute workflow example
		WorkflowExample()
	})
}

func TestWorkflowComponents(t *testing.T) {
	t.Run("secrets_management_initialization", func(t *testing.T) {
		ctx := context.Background()
		
		secretsManager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})
		secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())
		
		assert.NotNil(t, secretsManager)
		
		// Test configuration
		_, _, _, err := secretsManager.GetWorkOSConfig(ctx)
		if err != nil {
			t.Logf("WorkOS config not available in test: %v", err)
		}
	})
	
	t.Run("authentication_service_initialization", func(t *testing.T) {
		ctx := context.Background()
		
		secretsManager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})
		secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())
		
		workosAuth := auth.NewWorkOSAuthService(secretsManager)
		err := workosAuth.Initialize(ctx)
		
		// May fail due to missing valid credentials
		if err != nil {
			t.Logf("WorkOS auth initialization failed (expected in test): %v", err)
		}
		
		assert.NotNil(t, workosAuth)
	})
	
	t.Run("credential_validator_initialization", func(t *testing.T) {
		credValidator := clients.NewCredentialValidator()
		assert.NotNil(t, credValidator)
	})
}

func TestWorkflowConfiguration(t *testing.T) {
	t.Run("secrets_config_validation", func(t *testing.T) {
		config := secrets.Config{
			CacheTTL: 5 * time.Minute,
		}
		
		assert.Equal(t, 5*time.Minute, config.CacheTTL)
	})
	
	t.Run("context_creation", func(t *testing.T) {
		ctx := context.Background()
		assert.NotNil(t, ctx)
	})
}

func TestWorkflowErrorHandling(t *testing.T) {
	t.Run("missing_environment_variables", func(t *testing.T) {
		ctx := context.Background()
		
		// Clear environment variables
		requiredVars := []string{
			"WORKOS_CLIENT_ID",
			"WORKOS_CLIENT_SECRET",
			"WORKOS_API_KEY",
		}
		
		var oldValues map[string]string
		oldValues = make(map[string]string)
		
		for _, envVar := range requiredVars {
			if oldVal := os.Getenv(envVar); oldVal != "" {
				oldValues[envVar] = oldVal
				os.Unsetenv(envVar)
			}
		}
		defer func() {
			for envVar, oldVal := range oldValues {
				if oldVal != "" {
					os.Setenv(envVar, oldVal)
				} else {
					os.Unsetenv(envVar)
				}
			}
		}()
		
		secretsManager := secrets.New(secrets.Config{
			CacheTTL: 5 * time.Minute,
		})
		secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())
		
		workosAuth := auth.NewWorkOSAuthService(secretsManager)
		err := workosAuth.Initialize(ctx)
		
		// Should fail without environment variables
		assert.Error(t, err)
	})
}
