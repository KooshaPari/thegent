package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/byteport/api/testhelpers"
)

func TestHandleDeploy(t *testing.T) {
	// Setup test router
	router := testhelpers.TestRouter()

	// Mock deployment store adapter (since current code uses DeploymentStore)
	store := &DeploymentStore{
		deployments: make(map[string]*Deployment),
	}

	// Setup routes
	router.POST("/api/v1/deployments", handleDeploy(store))

	// Test cases using table-driven pattern
	testCases := []testhelpers.HTTPTestCase{
		{
			Name:   "Valid deployment request",
			Method: "POST",
			URL:    "/api/v1/deployments",
			Body: map[string]interface{}{
				"name":     "test-app",
				"type":     "frontend",
				"provider": "vercel",
				"git_url":  "https://github.com/test/app.git",
				"branch":   "main",
				"env_vars": map[string]string{
					"NODE_ENV": "production",
				},
			},
			ExpectedStatus: http.StatusCreated,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				// Custom validation
				testhelpers.CheckJSONStructure(t, resp, []string{
					"id", "name", "status", "provider", "created_at", "message",
				})

				var response map[string]interface{}
				testhelpers.ParseJSONResponse(t, resp, &response)

				if response["name"] != "test-app" {
					t.Errorf("Expected name 'test-app', got %v", response["name"])
				}
				if response["status"] != "deploying" {
					t.Errorf("Expected status 'deploying', got %v", response["status"])
				}
			},
		},
		{
			Name:   "Missing required name field",
			Method: "POST",
			URL:    "/api/v1/deployments",
			Body: map[string]interface{}{
				"type":     "frontend",
				"provider": "vercel",
			},
			ExpectedStatus: http.StatusBadRequest,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.AssertErrorResponse(t, resp, "Invalid request format")
			},
		},
		{
			Name:   "Missing required type field",
			Method: "POST",
			URL:    "/api/v1/deployments",
			Body: map[string]interface{}{
				"name":     "test-app",
				"provider": "vercel",
			},
			ExpectedStatus: http.StatusBadRequest,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.AssertErrorResponse(t, resp, "Invalid request format")
			},
		},
		{
			Name:   "Invalid provider",
			Method: "POST",
			URL:    "/api/v1/deployments",
			Body: map[string]interface{}{
				"name":     "test-app",
				"type":     "frontend",
				"provider": "invalid-provider",
			},
			ExpectedStatus: http.StatusBadRequest,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.AssertErrorResponse(t, resp, "Invalid provider")
			},
		},
		{
			Name:   "Auto-select provider when not specified",
			Method: "POST",
			URL:    "/api/v1/deployments",
			Body: map[string]interface{}{
				"name": "auto-provider-app",
				"type": "frontend",
				// No provider specified - should auto-select
			},
			ExpectedStatus: http.StatusCreated,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				var response map[string]interface{}
				testhelpers.ParseJSONResponse(t, resp, &response)

				// Should have auto-selected a provider
				if response["provider"] == nil || response["provider"] == "" {
					t.Error("Expected provider to be auto-selected")
				}
			},
		},
	}

	// Run all test cases
	testhelpers.RunHTTPTestCases(t, router, testCases)
}

func TestHandleListDeployments(t *testing.T) {
	router := testhelpers.TestRouter()
	store := &DeploymentStore{
		deployments: make(map[string]*Deployment),
	}

	// Pre-populate with test data
	testDeployments := []*Deployment{
		{
			ID:        "deploy-1",
			Name:      "App 1",
			Type:      "frontend",
			Provider:  "vercel",
			Status:    "deployed",
			URL:       "https://app1.vercel.app",
			CreatedAt: time.Now().Add(-24 * time.Hour),
		},
		{
			ID:        "deploy-2",
			Name:      "App 2",
			Type:      "backend",
			Provider:  "render",
			Status:    "failed",
			URL:       "",
			CreatedAt: time.Now().Add(-12 * time.Hour),
		},
	}

	for _, dep := range testDeployments {
		store.Add(dep)
	}

	router.GET("/api/v1/deployments", handleListDeployments(store))

	testCases := []testhelpers.HTTPTestCase{
		{
			Name:           "List all deployments",
			Method:         "GET",
			URL:            "/api/v1/deployments",
			ExpectedStatus: http.StatusOK,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.CheckJSONStructure(t, resp, []string{"deployments", "total"})

				var response map[string]interface{}
				testhelpers.ParseJSONResponse(t, resp, &response)

				deployments, ok := response["deployments"].([]interface{})
				if !ok {
					t.Error("Expected deployments to be an array")
					return
				}

				if len(deployments) != 2 {
					t.Errorf("Expected 2 deployments, got %d", len(deployments))
				}

				total, ok := response["total"].(float64)
				if !ok || int(total) != 2 {
					t.Errorf("Expected total to be 2, got %v", response["total"])
				}
			},
		},
	}

	testhelpers.RunHTTPTestCases(t, router, testCases)
}

func TestHandleGetDeployment(t *testing.T) {
	router := testhelpers.TestRouter()
	store := &DeploymentStore{
		deployments: make(map[string]*Deployment),
	}

	// Add test deployment
	testDeployment := &Deployment{
		ID:        "test-deployment-id",
		Name:      "Test App",
		Type:      "frontend",
		Provider:  "netlify",
		Status:    "deployed",
		URL:       "https://test-app.netlify.app",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	store.Add(testDeployment)

	router.GET("/api/v1/deployments/:id", handleGetDeployment(store))

	testCases := []testhelpers.HTTPTestCase{
		{
			Name:           "Get existing deployment",
			Method:         "GET",
			URL:            "/api/v1/deployments/test-deployment-id",
			ExpectedStatus: http.StatusOK,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				var deployment map[string]interface{}
				testhelpers.ParseJSONResponse(t, resp, &deployment)

				if deployment["id"] != "test-deployment-id" {
					t.Errorf("Expected id 'test-deployment-id', got %v", deployment["id"])
				}
				if deployment["name"] != "Test App" {
					t.Errorf("Expected name 'Test App', got %v", deployment["name"])
				}
			},
		},
		{
			Name:           "Get non-existent deployment",
			Method:         "GET",
			URL:            "/api/v1/deployments/non-existent-id",
			ExpectedStatus: http.StatusNotFound,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.AssertErrorResponse(t, resp, "Deployment not found")
			},
		},
	}

	testhelpers.RunHTTPTestCases(t, router, testCases)
}

func TestHandleTerminateDeployment(t *testing.T) {
	router := testhelpers.TestRouter()
	store := &DeploymentStore{
		deployments: make(map[string]*Deployment),
	}

	// Add test deployment
	testDeployment := &Deployment{
		ID:        "terminate-test-id",
		Name:      "App to Terminate",
		Type:      "backend",
		Provider:  "railway",
		Status:    "deployed",
		URL:       "https://app.railway.app",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	store.Add(testDeployment)

	router.DELETE("/api/v1/deployments/:id", handleTerminateDeployment(store))

	testCases := []testhelpers.HTTPTestCase{
		{
			Name:           "Terminate existing deployment",
			Method:         "DELETE",
			URL:            "/api/v1/deployments/terminate-test-id",
			ExpectedStatus: http.StatusOK,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.CheckJSONStructure(t, resp, []string{"message", "id"})

				// Verify deployment status was updated
				terminated := store.Get("terminate-test-id")
				if terminated == nil {
					t.Error("Expected deployment to still exist after termination")
				} else if terminated.Status != "terminated" {
					t.Errorf("Expected status 'terminated', got %s", terminated.Status)
				}
			},
		},
		{
			Name:           "Terminate non-existent deployment",
			Method:         "DELETE",
			URL:            "/api/v1/deployments/non-existent-id",
			ExpectedStatus: http.StatusNotFound,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				testhelpers.AssertErrorResponse(t, resp, "Deployment not found")
			},
		},
	}

	testhelpers.RunHTTPTestCases(t, router, testCases)
}
