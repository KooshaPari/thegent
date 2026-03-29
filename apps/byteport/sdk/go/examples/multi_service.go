package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"

	"github.com/byteport/sdk-go/byteport"
)

func main() {
	apiKey := os.Getenv("BYTEPORT_API_KEY")
	if apiKey == "" {
		log.Fatal("BYTEPORT_API_KEY environment variable not set")
	}

	client := byteport.NewClient(apiKey)
	ctx := context.Background()

	// Deploy multiple services concurrently
	var wg sync.WaitGroup
	deployments := make(map[string]*byteport.Deployment)
	errors := make(map[string]error)
	mutex := sync.Mutex{}

	services := []struct {
		name    string
		request *byteport.DeployRequest
	}{
		{
			name: "frontend",
			request: &byteport.DeployRequest{
				Name:   "my-frontend",
				Type:   "frontend",
				GitURL: "https://github.com/user/nextjs-app",
				EnvVars: map[string]string{
					"API_URL": "https://my-backend.onrender.com",
				},
			},
		},
		{
			name: "backend",
			request: &byteport.DeployRequest{
				Name:   "my-backend",
				Type:   "backend",
				GitURL: "https://github.com/user/express-api",
				EnvVars: map[string]string{
					"DATABASE_URL": "postgresql://user:pass@db:5432/myapp",
				},
			},
		},
		{
			name: "database",
			request: &byteport.DeployRequest{
				Name: "my-database",
				Type: "database",
				Config: map[string]interface{}{
					"engine":  "postgresql",
					"version": "15",
				},
			},
		},
	}

	fmt.Println("🚀 Deploying multi-service application...")

	for _, svc := range services {
		wg.Add(1)
		go func(name string, req *byteport.DeployRequest) {
			defer wg.Done()

			fmt.Printf("   Deploying %s...\n", name)
			deployment, err := client.Deploy(ctx, req)

			mutex.Lock()
			if err != nil {
				errors[name] = err
			} else {
				deployments[name] = deployment
			}
			mutex.Unlock()
		}(svc.name, svc.request)
	}

	wg.Wait()

	// Check for errors
	if len(errors) > 0 {
		fmt.Println("\n❌ Some deployments failed:")
		for name, err := range errors {
			fmt.Printf("   %s: %v\n", name, err)
		}
		os.Exit(1)
	}

	// Print results
	fmt.Println("\n✅ All services deployed successfully!\n")
	var totalCost float64
	for name, deployment := range deployments {
		fmt.Printf("📦 %s:\n", name)
		fmt.Printf("   ID: %s\n", deployment.ID)
		fmt.Printf("   URL: %s\n", deployment.URL)
		fmt.Printf("   Provider: %s\n", deployment.Provider)

		// Get metrics
		metrics, err := client.GetMetrics(ctx, deployment.ID)
		if err == nil {
			fmt.Printf("   Cost: $%.2f/month\n", metrics.Cost.Monthly)
			totalCost += metrics.Cost.Monthly
		}
		fmt.Println()
	}

	fmt.Printf("💰 Total monthly cost: $%.2f\n", totalCost)
}
