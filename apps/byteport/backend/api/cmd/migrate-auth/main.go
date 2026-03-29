//go:build tools
// +build tools

package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/byteport/api/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	var (
		databaseURL = flag.String("db", "", "Database URL (or set DATABASE_URL env var)")
		dryRun      = flag.Bool("dry-run", false, "Show what would be done without making changes")
		help        = flag.Bool("help", false, "Show help")
	)
	flag.Parse()

	if *help {
		printHelp()
		return
	}

	// Get database URL
	if *databaseURL == "" {
		*databaseURL = os.Getenv("DATABASE_URL")
	}
	if *databaseURL == "" {
		log.Fatal("Database URL is required. Use -db flag or set DATABASE_URL environment variable.")
	}

	fmt.Println("🚀 BytePort Authentication Migration Tool")
	fmt.Println("=========================================")

	if *dryRun {
		fmt.Println("🔍 DRY RUN MODE - No changes will be made")
	}

	// Connect to database
	db, err := gorm.Open(postgres.Open(*databaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Set global DB for models
	models.DB = db

	ctx := context.Background()

	// Run migration steps
	steps := []MigrationStep{
		{
			Name:        "Create WorkOS Users Table",
			Description: "Create the new workos_users table alongside existing users table",
			Function:    createWorkOSUsersTable,
		},
		{
			Name:        "Analyze Current User Data",
			Description: "Analyze existing user data for migration planning",
			Function:    analyzeCurrentUsers,
		},
		{
			Name:        "Prepare Migration Data",
			Description: "Prepare data for migration from legacy to WorkOS system",
			Function:    prepareMigrationData,
		},
		{
			Name:        "Validate Environment",
			Description: "Check that required environment variables are set",
			Function:    validateEnvironment,
		},
	}

	for i, step := range steps {
		fmt.Printf("\n📋 Step %d: %s\n", i+1, step.Name)
		fmt.Printf("   %s\n", step.Description)

		if *dryRun {
			fmt.Println("   ⏭️  Skipped (dry-run mode)")
			continue
		}

		if err := step.Function(ctx, db); err != nil {
			log.Fatalf("❌ Step %d failed: %v", i+1, err)
		}
		fmt.Println("   ✅ Completed")
	}

	fmt.Println("\n🎉 Migration preparation completed successfully!")
	fmt.Println("\n📝 Next Steps:")
	fmt.Println("   1. Review the migration plan above")
	fmt.Println("   2. Set up WorkOS environment variables:")
	fmt.Println("      - WORKOS_CLIENT_ID")
	fmt.Println("      - WORKOS_CLIENT_SECRET")
	fmt.Println("      - WORKOS_API_KEY")
	fmt.Println("   3. Update your application to use the consolidated auth handlers")
	fmt.Println("   4. Test the new authentication flow")
	fmt.Println("   5. Gradually migrate users by having them log in via WorkOS")
	fmt.Println("   6. Once all users are migrated, remove legacy auth code")
}
