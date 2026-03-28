package main

import (
	"byteport/api/handlers"
	"log"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	api := r.Group("/api")
	handlers.RegisterProviderRoutes(api)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Byteport API listening on :%s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
