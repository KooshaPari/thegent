//go:build examples
// +build examples

package examples

import (
	"context"
	"log"
	"time"

	"github.com/byteport/api/internal/infrastructure/auth"
	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/byteport/api/internal/infrastructure/secrets"
)

// WorkflowExample demonstrates a complete authentication workflow
func WorkflowExample() {
	ctx := context.Background()

	// Initialize secrets management
	secretsManager := secrets.New(secrets.Config{
		CacheTTL: 5 * time.Minute,
	})
	secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())

	// Initialize authentication service
	workosAuth := auth.NewWorkOSAuthService(secretsManager)
	_ = workosAuth.Initialize(ctx)

	// Initialize credential validator
	credValidator := clients.NewCredentialValidator()
	_ = credValidator

	log.Println("Workflow example completed")
}
