package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

// DeploymentHandlerTestSuite groups all deployment handler tests
type DeploymentHandlerTestSuite struct {
	suite.Suite
	router *gin.Engine
	store  *DeploymentStore
}

// SetupTest runs before each test
func (suite *DeploymentHandlerTestSuite) SetupTest() {
	gin.SetMode(gin.TestMode)
	suite.router = gin.New()
	suite.store = NewDeploymentStore()
	
	// Setup routes
	suite.router.POST("/api/v1/deployments", handleDeploy(suite.store))
	suite.router.GET("/api/v1/deployments", handleListDeployments(suite.store))
	suite.router.GET("/api/v1/deployments/:id", handleGetDeployment(suite.store))
	suite.router.DELETE("/api/v1/deployments/:id", handleTerminateDeployment(suite.store))
	suite.router.GET("/api/v1/deployments/:id/status", handleGetStatus(suite.store))
	suite.router.GET("/api/v1/deployments/:id/logs", handleGetLogs(suite.store))
}

// TestDeploymentCreate tests creating a new deployment
func (suite *DeploymentHandlerTestSuite) TestDeploymentCreate() {
	t := suite.T()
	
	t.Run("creates deployment with valid data", func(t *testing.T) {
		payload := DeployRequest{
			Name:     "test-app",
			Type:     "frontend",
			Provider: "vercel",
			GitURL:   "https://github.com/test/app.git",
			Branch:   "main",
			EnvVars: map[string]string{
				"NODE_ENV": "production",
			},
		}
		
		body, err := json.Marshal(payload)
		require.NoError(t, err)
		
		req := httptest.NewRequest(http.MethodPost, "/api/v1/deployments", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response DeployResponse
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		
		assert.NotEmpty(t, response.ID)
		assert.Equal(t, "test-app", response.Name)
		assert.Equal(t, "deploying", response.Status)
		assert.Equal(t, "vercel", response.Provider)
		assert.NotEmpty(t, response.URL)
		assert.Contains(t, response.Message, "successfully")
	})
	
	t.Run("fails with missing name", func(t *testing.T) {
		payload := DeployRequest{
			Type:     "frontend",
			Provider: "vercel",
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/deployments", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var errorResp map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &errorResp)
		assert.Contains(t, errorResp["error"], "Invalid request")
	})
	
	t.Run("fails with missing type", func(t *testing.T) {
		payload := DeployRequest{
			Name:     "test-app",
			Provider: "vercel",
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/deployments", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
	
	t.Run("auto-selects provider when not specified", func(t *testing.T) {
		payload := DeployRequest{
			Name: "auto-provider-app",
			Type: "frontend",
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/deployments", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response DeployResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.NotEmpty(t, response.Provider)
	})
	
	t.Run("rejects invalid provider", func(t *testing.T) {
		payload := DeployRequest{
			Name:     "test-app",
			Type:     "frontend",
			Provider: "invalid-provider",
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/deployments", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var errorResp map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &errorResp)
		assert.Contains(t, errorResp["error"], "Invalid provider")
		assert.Contains(t, errorResp, "valid_providers")
	})
}

// TestDeploymentList tests listing deployments
func (suite *DeploymentHandlerTestSuite) TestDeploymentList() {
	t := suite.T()
	
	t.Run("returns empty list when no deployments", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		
		deployments := response["deployments"].([]interface{})
		total := response["total"].(float64)
		
		assert.Equal(t, 0, len(deployments))
		assert.Equal(t, float64(0), total)
	})
	
	t.Run("returns all deployments", func(t *testing.T) {
		// Add test deployments
		suite.store.Add(&Deployment{
			ID:        "deploy-1",
			Name:      "App 1",
			Type:      "frontend",
			Provider:  "vercel",
			Status:    "deployed",
			URL:       "https://app1.vercel.app",
			CreatedAt: time.Now(),
		})
		suite.store.Add(&Deployment{
			ID:        "deploy-2",
			Name:      "App 2",
			Type:      "backend",
			Provider:  "render",
			Status:    "failed",
			CreatedAt: time.Now(),
		})
		
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		
		deployments := response["deployments"].([]interface{})
		total := response["total"].(float64)
		
		assert.Equal(t, 2, len(deployments))
		assert.Equal(t, float64(2), total)
	})
}

// TestDeploymentGet tests getting a specific deployment
func (suite *DeploymentHandlerTestSuite) TestDeploymentGet() {
	t := suite.T()
	
	t.Run("returns deployment by ID", func(t *testing.T) {
		deployment := &Deployment{
			ID:        "test-id-123",
			Name:      "Test App",
			Type:      "frontend",
			Provider:  "netlify",
			Status:    "deployed",
			URL:       "https://test-app.netlify.app",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		suite.store.Add(deployment)
		
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/test-id-123", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response Deployment
		json.Unmarshal(w.Body.Bytes(), &response)
		
		assert.Equal(t, "test-id-123", response.ID)
		assert.Equal(t, "Test App", response.Name)
		assert.Equal(t, "deployed", response.Status)
	})
	
	t.Run("returns 404 for non-existent deployment", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/non-existent", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNotFound, w.Code)
		
		var errorResp map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &errorResp)
		assert.Contains(t, errorResp["error"], "not found")
	})
}

// TestDeploymentTerminate tests terminating a deployment
func (suite *DeploymentHandlerTestSuite) TestDeploymentTerminate() {
	t := suite.T()
	
	t.Run("terminates existing deployment", func(t *testing.T) {
		deployment := &Deployment{
			ID:        "terminate-id",
			Name:      "App to Terminate",
			Type:      "backend",
			Provider:  "railway",
			Status:    "deployed",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		suite.store.Add(deployment)
		
		req := httptest.NewRequest(http.MethodDelete, "/api/v1/deployments/terminate-id", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Contains(t, response["message"], "terminated")
		
		// Verify status was updated
		terminated := suite.store.Get("terminate-id")
		require.NotNil(t, terminated)
		assert.Equal(t, "terminated", terminated.Status)
	})
	
	t.Run("returns 404 for non-existent deployment", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodDelete, "/api/v1/deployments/non-existent", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}

// TestDeploymentStatus tests getting deployment status
func (suite *DeploymentHandlerTestSuite) TestDeploymentStatus() {
	t := suite.T()
	
	t.Run("returns deployment status", func(t *testing.T) {
		deployment := &Deployment{
			ID:        "status-id",
			Name:      "Status Test App",
			Status:    "deployed",
			UpdatedAt: time.Now(),
		}
		suite.store.Add(deployment)
		
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/status-id/status", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		
		assert.Equal(t, "status-id", response["id"])
		assert.Equal(t, "deployed", response["status"])
		assert.NotNil(t, response["progress"])
		assert.NotNil(t, response["updated_at"])
	})
}

// TestDeploymentLogs tests getting deployment logs
func (suite *DeploymentHandlerTestSuite) TestDeploymentLogs() {
	t := suite.T()
	
	t.Run("returns deployment logs", func(t *testing.T) {
		deployment := &Deployment{
			ID:   "logs-id",
			Name: "Logs Test App",
		}
		suite.store.Add(deployment)
		
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/logs-id/logs", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		// Response should contain logs array
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.NotNil(t, response)
	})
	
	t.Run("returns 404 for non-existent deployment", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/deployments/non-existent/logs", nil)
		w := httptest.NewRecorder()
		
		suite.router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}

// Run the test suite
func TestDeploymentHandlerTestSuite(t *testing.T) {
	suite.Run(t, new(DeploymentHandlerTestSuite))
}