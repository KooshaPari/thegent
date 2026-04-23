// Package middleware provides HTTP middleware for the Byteport API server.
package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
)

// LoggingMiddleware returns a gin middleware that logs each request's
// method, path, status, duration, and response size via the provided
// structured logger.
func LoggingMiddleware(logger *slog.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		logger.Info("http.request",
			slog.String("method", c.Request.Method),
			slog.String("path", c.Request.URL.Path),
			slog.Int("status", c.Writer.Status()),
			slog.Int("bytes", c.Writer.Size()),
			slog.Duration("duration", time.Since(start)),
			slog.String("client_ip", c.ClientIP()),
		)
	}
}
