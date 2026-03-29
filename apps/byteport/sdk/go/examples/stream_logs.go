package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/byteport/sdk-go/byteport"
)

func main() {
	apiKey := os.Getenv("BYTEPORT_API_KEY")
	if apiKey == "" {
		log.Fatal("BYTEPORT_API_KEY environment variable not set")
	}

	if len(os.Args) < 2 {
		log.Fatal("Usage: stream_logs <deployment_id>")
	}

	deploymentID := os.Args[1]
	client := byteport.NewClient(apiKey)

	// Create context with cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Handle interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sigChan
		fmt.Println("\n\n🛑 Stopping log stream...")
		cancel()
	}()

	fmt.Printf("📜 Streaming logs for deployment: %s\n", deploymentID)
	fmt.Println("Press Ctrl+C to stop\n")

	// Stream logs
	logChan, errChan, err := client.StreamLogs(ctx, deploymentID)
	if err != nil {
		log.Fatalf("Failed to stream logs: %v", err)
	}

	// Process logs
	for {
		select {
		case logEntry, ok := <-logChan:
			if !ok {
				fmt.Println("\n✅ Log stream ended")
				return
			}
			fmt.Printf("[%s] [%s] %s\n",
				logEntry.Timestamp.Format("15:04:05"),
				logEntry.Level,
				logEntry.Message)

		case err, ok := <-errChan:
			if ok && err != nil {
				log.Printf("❌ Stream error: %v", err)
			}
			return

		case <-ctx.Done():
			return
		}
	}
}
