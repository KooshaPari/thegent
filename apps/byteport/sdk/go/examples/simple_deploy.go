package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/byteport/sdk-go/byteport"
)

func main() {
	// Get API key from environment
	apiKey := os.Getenv("BYTEPORT_API_KEY")
	if apiKey == "" {
		log.Fatal("BYTEPORT_API_KEY environment variable not set")
	}

	// Create client
	client := byteport.NewClient(apiKey)

	// Deploy Next.js app
	deployment, err := client.Deploy(context.Background(), &byteport.DeployRequest{
		Name:   "my-nextjs-app",
		Type:   "frontend",
		GitURL: "https://github.com/user/nextjs-app",
		EnvVars: map[string]string{
			"API_URL": "https://api.example.com",
		},
	})

	if err != nil {
		log.Fatalf("Deployment failed: %v", err)
	}

	fmt.Printf("✅ Deployment created successfully!\n")
	fmt.Printf("   ID: %s\n", deployment.ID)
	fmt.Printf("   Name: %s\n", deployment.Name)
	fmt.Printf("   Status: %s\n", deployment.Status)
	fmt.Printf("   URL: %s\n", deployment.URL)
	fmt.Printf("   Provider: %s\n", deployment.Provider)

	// Wait for deployment to complete
	fmt.Println("\n⏳ Waiting for deployment to complete...")
	finalDeployment, err := client.WaitForDeployment(context.Background(), deployment.ID)
	if err != nil {
		log.Fatalf("Failed to wait for deployment: %v", err)
	}

	if finalDeployment.Status == "deployed" {
		fmt.Printf("\n✅ Deployment successful!\n")
		fmt.Printf("   Live URL: %s\n", finalDeployment.URL)
	} else {
		fmt.Printf("\n❌ Deployment failed with status: %s\n", finalDeployment.Status)
	}
}
