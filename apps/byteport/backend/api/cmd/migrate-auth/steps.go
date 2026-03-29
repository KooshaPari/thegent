//go:build tools
// +build tools

package main

import (
	"context"
	"fmt"
	"os"

	"github.com/byteport/api/models"
	"gorm.io/gorm"
)

type MigrationStep struct {
	Name        string
	Description string
	Function    func(context.Context, *gorm.DB) error
}

func createWorkOSUsersTable(ctx context.Context, db *gorm.DB) error {
	// Create the WorkOSUser table
	if err := db.AutoMigrate(&models.WorkOSUser{}); err != nil {
		return fmt.Errorf("failed to create workos_users table: %w", err)
	}

	fmt.Println("   📊 WorkOS users table created/updated")
	return nil
}

func analyzeCurrentUsers(ctx context.Context, db *gorm.DB) error {
	var userCount int64
	if err := db.Model(&models.User{}).Count(&userCount).Error; err != nil {
		return fmt.Errorf("failed to count users: %w", err)
	}

	var usersWithCredentials int64
	if err := db.Model(&models.User{}).
		Where("aws_access_key_id != '' OR llm_providers != '{}' OR portfolio_api_key != ''").
		Count(&usersWithCredentials).Error; err != nil {
		return fmt.Errorf("failed to count users with credentials: %w", err)
	}

	fmt.Printf("   📊 Found %d total users\n", userCount)
	fmt.Printf("   🔑 %d users have stored credentials that need migration\n", usersWithCredentials)

	if usersWithCredentials > 0 {
		fmt.Println("   ⚠️  Users have stored credentials - you'll need to implement credential migration")
		fmt.Println("       Consider moving these to environment variables or external secret management")
	}

	return nil
}

func prepareMigrationData(ctx context.Context, db *gorm.DB) error {
	// Check if there are any existing WorkOS users
	var workosUserCount int64
	if err := db.Model(&models.WorkOSUser{}).Count(&workosUserCount).Error; err != nil {
		// Table might not exist yet, that's okay
		workosUserCount = 0
	}

	fmt.Printf("   📊 Found %d existing WorkOS users\n", workosUserCount)

	// Sample migration logic (commented out for safety)
	fmt.Println("   📝 Migration strategy:")
	fmt.Println("      - New users will be created directly in workos_users table")
	fmt.Println("      - Existing users will be migrated on first WorkOS login")
	fmt.Println("      - Both user tables will coexist during transition period")

	return nil
}

func validateEnvironment(ctx context.Context, db *gorm.DB) error {
	requiredEnvVars := []string{
		"WORKOS_CLIENT_ID",
		"WORKOS_CLIENT_SECRET",
		"WORKOS_API_KEY",
	}

	optionalEnvVars := []string{
		"OPENAI_API_KEY",
		"AWS_ACCESS_KEY_ID",
		"AWS_SECRET_ACCESS_KEY",
		"PORTFOLIO_API_KEY",
		"PORTFOLIO_ROOT_ENDPOINT",
	}

	fmt.Println("   🔍 Required environment variables:")
	allRequired := true
	for _, envVar := range requiredEnvVars {
		if value := os.Getenv(envVar); value != "" {
			fmt.Printf("      ✅ %s: configured\n", envVar)
		} else {
			fmt.Printf("      ❌ %s: NOT SET\n", envVar)
			allRequired = false
		}
	}

	fmt.Println("   🔍 Optional environment variables:")
	for _, envVar := range optionalEnvVars {
		if value := os.Getenv(envVar); value != "" {
			fmt.Printf("      ✅ %s: configured\n", envVar)
		} else {
			fmt.Printf("      ⚠️  %s: not set\n", envVar)
		}
	}

	if !allRequired {
		fmt.Println("   ⚠️  Some required environment variables are missing")
		fmt.Println("      Set these before using the consolidated auth system")
	}

	return nil
}

func printHelp() {
	fmt.Println("BytePort Authentication Migration Tool")
	fmt.Println("=====================================")
	fmt.Println()
	fmt.Println("This tool helps migrate from the legacy authentication system")
	fmt.Println("to the new consolidated WorkOS AuthKit system.")
	fmt.Println()
	fmt.Println("Usage:")
	fmt.Println("  go run cmd/migrate-auth/main.go [flags]")
	fmt.Println()
	fmt.Println("Flags:")
	fmt.Println("  -db string      Database URL (or set DATABASE_URL env var)")
	fmt.Println("  -dry-run        Show what would be done without making changes")
	fmt.Println("  -help           Show this help message")
	fmt.Println()
	fmt.Println("Environment Variables:")
	fmt.Println("  DATABASE_URL              PostgreSQL connection string")
	fmt.Println("  WORKOS_CLIENT_ID          WorkOS client ID")
	fmt.Println("  WORKOS_CLIENT_SECRET      WorkOS client secret")
	fmt.Println("  WORKOS_API_KEY            WorkOS API key")
	fmt.Println()
	fmt.Println("Examples:")
	fmt.Println("  # Dry run to see what would happen")
	fmt.Println("  go run cmd/migrate-auth/main.go -dry-run")
	fmt.Println()
	fmt.Println("  # Run actual migration")
	fmt.Println("  DATABASE_URL=postgres://... go run cmd/migrate-auth/main.go")
}
