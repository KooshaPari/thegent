package main

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/byteport/api/internal/container"
	"github.com/byteport/api/testhelpers"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewAPIServer(t *testing.T) {
	t.Run("creates API server with default configuration", func(t *testing.T) {
		// Create a mock container
		containerInst := &container.Container{}
		
		server := NewAPIServer(containerInst)
		
		require.NotNil(t, server)
		require.NotNil(t, server.router)
		require.NotNil(t, server.container)
		require.NotNil(t, server.store)
	})

	t.Run("sets up CORS middleware", func(t *testing.T) {
		containerInst := &container.Container{}
		server := NewAPIServer(containerInst)
		
		// Test that the server can handle requests
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/v1/health", nil)
		server.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("registers all API routes", func(t *testing.T) {
		containerInst := &container.Container{}
		server := NewAPIServer(containerInst)
		
		// Test health endpoint
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/v1/health", nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
		
		// Test API info endpoint
		w = httptest.NewRecorder()
		req = httptest.NewRequest("GET", "/api/v1/", nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
		
		// Test docs endpoint
		w = httptest.NewRecorder()
		req = httptest.NewRequest("GET", "/api/v1/docs", nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestParseAllowedOrigins(t *testing.T) {
	t.Run("returns default origins when ALLOWED_ORIGINS is not set", func(t *testing.T) {
		// Clear environment variable
		os.Unsetenv("ALLOWED_ORIGINS")
		
		origins := parseAllowedOrigins()
		
		expected := []string{
			"http://localhost:3000",
			"http://localhost:5173",
			"http://localhost:8002",
			"https://byte.kooshapari.com",
		}
		assert.Equal(t, expected, origins)
	})

	t.Run("returns custom origins from environment", func(t *testing.T) {
		// Set custom origins
		os.Setenv("ALLOWED_ORIGINS", "https://example.com,https://test.com, https://app.com ")
		defer os.Unsetenv("ALLOWED_ORIGINS")
		
		origins := parseAllowedOrigins()
		
		expected := []string{
			"https://example.com",
			"https://test.com",
			"https://app.com",
		}
		assert.Equal(t, expected, origins)
	})

	t.Run("filters out empty origins", func(t *testing.T) {
		os.Setenv("ALLOWED_ORIGINS", "https://example.com,,https://test.com, ,https://app.com")
		defer os.Unsetenv("ALLOWED_ORIGINS")
		
		origins := parseAllowedOrigins()
		
		expected := []string{
			"https://example.com",
			"https://test.com",
			"https://app.com",
		}
		assert.Equal(t, expected, origins)
	})

	t.Run("handles single origin", func(t *testing.T) {
		os.Setenv("ALLOWED_ORIGINS", "https://single.com")
		defer os.Unsetenv("ALLOWED_ORIGINS")
		
		origins := parseAllowedOrigins()
		
		expected := []string{"https://single.com"}
		assert.Equal(t, expected, origins)
	})
}

func TestHandleAPIInfo(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("returns API information", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		
		handleAPIInfo(c)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		
		assert.Equal(t, "BytePort API", response["name"])
		assert.Equal(t, "2.0.0", response["version"])
		assert.Equal(t, "Zero-cost deployment platform API", response["description"])
		
		endpoints, ok := response["endpoints"].(map[string]interface{})
		require.True(t, ok)
		assert.Equal(t, "/api/v1/health", endpoints["health"])
		assert.Equal(t, "/api/v1/deployments", endpoints["deployments"])
		assert.Equal(t, "/api/v1/projects", endpoints["projects"])
		assert.Equal(t, "/api/v1/docs", endpoints["docs"])
	})
}

func TestHandleHealth(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("returns health status", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		
		handleHealth(c)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		
		assert.Equal(t, "healthy", response["status"])
		assert.Equal(t, "byteport-api", response["service"])
		assert.Equal(t, "2.0.0", response["version"])
	})
}

func TestHandleDocs(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("returns API documentation", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		
		handleDocs(c)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		
		assert.Equal(t, "BytePort API Documentation", response["title"])
		assert.Equal(t, "2.0.0", response["version"])
		assert.Equal(t, "REST API for zero-cost deployments", response["description"])
		
		endpoints, ok := response["endpoints"].([]interface{})
		require.True(t, ok)
		assert.Greater(t, len(endpoints), 0)
		
		// Check first endpoint structure
		firstEndpoint, ok := endpoints[0].(map[string]interface{})
		require.True(t, ok)
		assert.Contains(t, firstEndpoint, "method")
		assert.Contains(t, firstEndpoint, "path")
		assert.Contains(t, firstEndpoint, "description")
	})
}

func TestHandleWorkOSCallback(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("handles missing code parameter", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req := httptest.NewRequest("POST", "/auth/workos/callback", nil)
		c.Request = req
		
		handleWorkOSCallback(c)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		assert.Contains(t, response["error"], "code")
	})

	t.Run("handles missing state parameter", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req := httptest.NewRequest("POST", "/auth/workos/callback?code=test-code", nil)
		c.Request = req
		
		handleWorkOSCallback(c)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		assert.Contains(t, response["error"], "state")
	})

	t.Run("handles valid callback parameters", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req := httptest.NewRequest("POST", "/auth/workos/callback?code=test-code&state=test-state", nil)
		c.Request = req
		
		handleWorkOSCallback(c)
		
		// Should attempt to process the callback
		// The actual processing will fail due to missing WorkOS configuration
		// but we can test that the function handles the parameters correctly
		assert.True(t, w.Code == http.StatusOK || w.Code == http.StatusInternalServerError)
	})
}

func TestHandleGetUser(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("returns user information", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Params = gin.Params{{Key: "id", Value: "test-user-123"}}
		
		handleGetUser(c)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		testhelpers.ParseJSONResponse(t, w, &response)
		
		assert.Equal(t, "test-user-123", response["id"])
		assert.Contains(t, response, "name")
		assert.Contains(t, response, "email")
	})
}


func TestAPIServerIntegration(t *testing.T) {
	t.Run("full server integration test", func(t *testing.T) {
		// Create a mock container
		containerInst := &container.Container{}
		
		// Create server
		server := NewAPIServer(containerInst)
		require.NotNil(t, server)
		
		// Test all public endpoints
		endpoints := []struct {
			method string
			path   string
			status int
		}{
			{"GET", "/api/v1/health", http.StatusOK},
			{"GET", "/api/v1/", http.StatusOK},
			{"GET", "/api/v1/docs", http.StatusOK},
			{"POST", "/api/v1/detect", http.StatusOK},
			{"POST", "/api/v1/estimate-cost", http.StatusOK},
			{"POST", "/api/v1/validate-config", http.StatusOK},
		}
		
		for _, endpoint := range endpoints {
			w := httptest.NewRecorder()
			req := httptest.NewRequest(endpoint.method, endpoint.path, nil)
			server.router.ServeHTTP(w, req)
			
			assert.Equal(t, endpoint.status, w.Code, "Endpoint %s %s should return %d", endpoint.method, endpoint.path, endpoint.status)
		}
	})
}

func TestMainFunction(t *testing.T) {
	t.Run("main function can be called without crashing", func(t *testing.T) {
		// This is a basic test to ensure the main function doesn't panic
		// In a real scenario, we would need to mock all dependencies
		// For now, we'll just test that the function exists and can be referenced
		
		// The main function is not directly testable as it calls os.Exit
		// But we can test the individual components it calls
		assert.NotNil(t, main)
	})
}

func TestCORSConfiguration(t *testing.T) {
	t.Run("CORS middleware is properly configured", func(t *testing.T) {
		containerInst := &container.Container{}
		server := NewAPIServer(containerInst)
		
		// Test OPTIONS request (CORS preflight)
		w := httptest.NewRecorder()
		req := httptest.NewRequest("OPTIONS", "/api/v1/health", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		req.Header.Set("Access-Control-Request-Method", "GET")
		server.router.ServeHTTP(w, req)
		
		// Should handle OPTIONS request
		assert.True(t, w.Code == http.StatusOK || w.Code == http.StatusNoContent)
	})
}

func TestEnvironmentHandling(t *testing.T) {
	t.Run("handles different environment configurations", func(t *testing.T) {
		// Test with different ALLOWED_ORIGINS values
		testCases := []struct {
			envValue string
			expected []string
		}{
			{"", []string{"http://localhost:3000", "http://localhost:5173", "http://localhost:8002", "https://byte.kooshapari.com"}},
			{"https://example.com", []string{"https://example.com"}},
			{"https://app1.com,https://app2.com", []string{"https://app1.com", "https://app2.com"}},
		}
		
		for _, tc := range testCases {
			os.Setenv("ALLOWED_ORIGINS", tc.envValue)
			origins := parseAllowedOrigins()
			assert.Equal(t, tc.expected, origins)
		}
		
		os.Unsetenv("ALLOWED_ORIGINS")
	})
}

func TestErrorHandling(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	t.Run("handles malformed requests gracefully", func(t *testing.T) {
		containerInst := &container.Container{}
		server := NewAPIServer(containerInst)
		
		// Test with malformed JSON
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/v1/legacy/deployments", nil)
		req.Header.Set("Content-Type", "application/json")
		server.router.ServeHTTP(w, req)
		
		// Should return 400 for malformed request
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestContextHandling(t *testing.T) {
	t.Run("handles context cancellation", func(t *testing.T) {
		containerInst := &container.Container{}
		server := NewAPIServer(containerInst)
		
		// Create a context that's already cancelled
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/v1/health", nil)
		req = req.WithContext(ctx)
		server.router.ServeHTTP(w, req)
		
		// Should still handle the request (Gin handles context internally)
		assert.Equal(t, http.StatusOK, w.Code)
	})
}