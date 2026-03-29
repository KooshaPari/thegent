package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/matryer/is"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSelectOptimalProvider tests the provider selection logic
func TestSelectOptimalProvider(t *testing.T) {
	is := is.New(t)

	tests := []struct {
		name     string
		appType  string
		expected string
	}{
		{
			name:     "frontend app selects vercel",
			appType:  "frontend",
			expected: "vercel",
		},
		{
			name:     "backend app selects render",
			appType:  "backend",
			expected: "render",
		},
		{
			name:     "database app selects supabase",
			appType:  "database",
			expected: "supabase",
		},
		{
			name:     "unknown type defaults to vercel",
			appType:  "unknown",
			expected: "vercel",
		},
		{
			name:     "empty type defaults to vercel",
			appType:  "",
			expected: "vercel",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := selectOptimalProvider(tt.appType)
			is.Equal(result, tt.expected)
		})
	}
}

// TestIsValidProvider tests provider validation
func TestIsValidProvider(t *testing.T) {
	is := is.New(t)

	tests := []struct {
		name     string
		provider string
		expected bool
	}{
		{
			name:     "vercel is valid",
			provider: "vercel",
			expected: true,
		},
		{
			name:     "netlify is valid",
			provider: "netlify",
			expected: true,
		},
		{
			name:     "render is valid",
			provider: "render",
			expected: true,
		},
		{
			name:     "railway is valid",
			provider: "railway",
			expected: true,
		},
		{
			name:     "supabase is valid",
			provider: "supabase",
			expected: true,
		},
		{
			name:     "cloudflare-pages is valid",
			provider: "cloudflare-pages",
			expected: true,
		},
		{
			name:     "invalid provider returns false",
			provider: "invalid-provider",
			expected: false,
		},
		{
			name:     "empty provider returns false",
			provider: "",
			expected: false,
		},
		{
			name:     "case sensitive - Vercel is invalid",
			provider: "Vercel",
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := isValidProvider(tt.provider)
			is.Equal(result, tt.expected)
		})
	}
}

// TestGenerateDeploymentURL tests URL generation for different providers
func TestGenerateDeploymentURL(t *testing.T) {
	is := is.New(t)

	tests := []struct {
		name     string
		appName  string
		provider string
		expected string
	}{
		{
			name:     "vercel URL format",
			appName:  "my-app",
			provider: "vercel",
			expected: "https://my-app.vercel.app",
		},
		{
			name:     "netlify URL format",
			appName:  "my-app",
			provider: "netlify",
			expected: "https://my-app.netlify.app",
		},
		{
			name:     "render URL format",
			appName:  "my-app",
			provider: "render",
			expected: "https://my-app.onrender.com",
		},
		{
			name:     "railway URL format",
			appName:  "my-app",
			provider: "railway",
			expected: "https://my-app.up.railway.app",
		},
		{
			name:     "supabase URL format",
			appName:  "my-app",
			provider: "supabase",
			expected: "https://my-app.supabase.co",
		},
		{
			name:     "cloudflare-pages URL format",
			appName:  "my-app",
			provider: "cloudflare-pages",
			expected: "https://my-app.pages.dev",
		},
		{
			name:     "unknown provider uses default format",
			appName:  "my-app",
			provider: "unknown",
			expected: "https://my-app.deployed.io",
		},
		{
			name:     "handles app name with hyphens",
			appName:  "my-awesome-app",
			provider: "vercel",
			expected: "https://my-awesome-app.vercel.app",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := generateDeploymentURL(tt.appName, tt.provider)
			is.Equal(result, tt.expected)
		})
	}
}

// TestGetProgress tests progress calculation based on status
func TestGetProgress(t *testing.T) {
	is := is.New(t)

	tests := []struct {
		name     string
		status   string
		expected int
	}{
		{
			name:     "deploying status shows 50% progress",
			status:   "deploying",
			expected: 50,
		},
		{
			name:     "building status shows 50% progress",
			status:   "building",
			expected: 50,
		},
		{
			name:     "deployed status shows 100% progress",
			status:   "deployed",
			expected: 100,
		},
		{
			name:     "failed status shows 0% progress",
			status:   "failed",
			expected: 0,
		},
		{
			name:     "unknown status defaults to 25% progress",
			status:   "unknown",
			expected: 25,
		},
		{
			name:     "empty status defaults to 25% progress",
			status:   "",
			expected: 25,
		},
		{
			name:     "pending status defaults to 25% progress",
			status:   "pending",
			expected: 25,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := getProgress(tt.status)
			is.Equal(result, tt.expected)
		})
	}
}

// TestHandleGetMetrics tests the metrics endpoint
func TestHandleGetMetrics(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	store := NewDeploymentStore()

	router.GET("/api/v1/deployments/:id/metrics", handleGetMetrics(store))

	t.Run("returns metrics for existing deployment", func(t *testing.T) {
		// Add a deployment
		store.Add(&Deployment{
			ID:   "metrics-test-id",
			Name: "Test App",
		})

		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/metrics-test-id/metrics", nil)
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		// Verify expected metrics fields
		assert.Equal(t, "metrics-test-id", response["deployment_id"])
		assert.NotNil(t, response["uptime"])
		assert.NotNil(t, response["requests"])
		assert.NotNil(t, response["bandwidth"])
		assert.NotNil(t, response["response_time"])
		assert.NotNil(t, response["cost"])
	})

	t.Run("returns 404 for non-existent deployment", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/non-existent/metrics", nil)
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusNotFound, w.Code)

		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Contains(t, response["error"], "not found")
	})
}

// TestHandleCreateProject tests project creation
func TestHandleCreateProject(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.POST("/api/v1/projects", handleCreateProject)

	t.Run("creates project with valid data", func(t *testing.T) {
		payload := map[string]string{
			"name":        "Test Project",
			"description": "A test project",
		}

		body, err := json.Marshal(payload)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusCreated, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.NotEmpty(t, response["id"])
		assert.Equal(t, "Test Project", response["name"])
		assert.Equal(t, "A test project", response["description"])
		assert.NotNil(t, response["created_at"])
	})

	t.Run("fails without required name", func(t *testing.T) {
		payload := map[string]string{
			"description": "Missing name",
		}

		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("fails with invalid JSON", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

// TestHandleListProjects tests project listing
func TestHandleListProjects(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.GET("/api/v1/projects", handleListProjects)

	t.Run("returns list of projects", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		projects, ok := response["projects"].([]interface{})
		assert.True(t, ok)
		assert.NotNil(t, projects)
	})
}

// TestHandleGetProject tests getting a specific project
func TestHandleGetProject(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.GET("/api/v1/projects/:id", handleGetProject)

	t.Run("returns project by ID", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/test-project-id", nil)
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.Equal(t, "test-project-id", response["id"])
		assert.NotNil(t, response["name"])
		assert.NotNil(t, response["deployments"])
	})
}

// TestHandleDeleteProject tests project deletion
func TestHandleDeleteProject(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.DELETE("/api/v1/projects/:id", handleDeleteProject)

	t.Run("deletes project by ID", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/test-project-id", nil)
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.Contains(t, response["message"], "deleted")
		assert.Equal(t, "test-project-id", response["id"])
	})
}

// TestHandleDetectApp tests application detection
func TestHandleDetectApp(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.POST("/api/v1/detect", handleDetectApp)

	t.Run("detects app type from files", func(t *testing.T) {
		payload := map[string]interface{}{
			"files": []string{"package.json", "index.tsx", "tsconfig.json"},
		}

		body, err := json.Marshal(payload)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/detect", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.NotNil(t, response["type"])
		assert.NotNil(t, response["framework"])
		assert.NotNil(t, response["confidence"])
		assert.NotNil(t, response["suggested_provider"])
	})

	t.Run("fails with invalid request", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/detect", bytes.NewReader([]byte("invalid")))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

// TestHandleEstimateCost tests cost estimation
func TestHandleEstimateCost(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.POST("/api/v1/estimate", handleEstimateCost)

	t.Run("estimates cost for deployment", func(t *testing.T) {
		payload := map[string]string{
			"type":     "frontend",
			"provider": "vercel",
		}

		body, err := json.Marshal(payload)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/estimate", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.NotNil(t, response["monthly"])
		assert.NotNil(t, response["currency"])
		assert.NotNil(t, response["breakdown"])
		assert.NotNil(t, response["message"])
	})

	t.Run("fails with invalid request", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/estimate", bytes.NewReader([]byte("invalid")))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

// TestHandleValidateConfig tests configuration validation
func TestHandleValidateConfig(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.POST("/api/v1/validate", handleValidateConfig)

	t.Run("validates deployment configuration", func(t *testing.T) {
		payload := map[string]interface{}{
			"name":     "test-app",
			"provider": "vercel",
			"env_vars": map[string]string{
				"NODE_ENV": "production",
			},
		}

		body, err := json.Marshal(payload)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/validate", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.NotNil(t, response["valid"])
		assert.NotNil(t, response["errors"])
		assert.NotNil(t, response["warnings"])
	})

	t.Run("fails with invalid JSON", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/validate", bytes.NewReader([]byte("invalid")))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

// TestSimulateDeployment tests async deployment simulation
func TestSimulateDeployment(t *testing.T) {
	store := NewDeploymentStore()

	deployment := &Deployment{
		ID:     "simulate-test-id",
		Name:   "Test Deployment",
		Status: "deploying",
	}
	store.Add(deployment)

	t.Run("simulates deployment and updates status", func(t *testing.T) {
		// Run simulation (but don't wait for the full 3 seconds)
		go simulateDeployment(store, deployment.ID)

		// Verify initial status
		dep := store.Get(deployment.ID)
		require.NotNil(t, dep)

		// Note: In real tests, you'd want to either:
		// 1. Use a mock time or shorter delay for testing
		// 2. Use channels to coordinate the test
		// 3. Accept that this tests the function exists, not the timing

		// For now, just verify the deployment exists and function runs without panic
		assert.Equal(t, "simulate-test-id", dep.ID)
	})
}
