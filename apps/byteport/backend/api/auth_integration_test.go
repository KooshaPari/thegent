//go:build !integration

package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAuthHandlersIntegration(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	// Set up environment for testing
	os.Setenv("WORKOS_CLIENT_ID", "test-client-id")
	os.Setenv("WORKOS_CLIENT_SECRET", "test-client-secret")
	os.Setenv("WORKOS_API_KEY", "test-api-key")
	os.Setenv("OPENAI_API_KEY", "test-openai-key")
	os.Setenv("AWS_ACCESS_KEY_ID", "test-aws-key")
	os.Setenv("AWS_SECRET_ACCESS_KEY", "test-aws-secret")
	os.Setenv("PORTFOLIO_API_KEY", "test-portfolio-key")
	os.Setenv("PORTFOLIO_ROOT_ENDPOINT", "https://test.com")
	
	defer func() {
		os.Unsetenv("WORKOS_CLIENT_ID")
		os.Unsetenv("WORKOS_CLIENT_SECRET")
		os.Unsetenv("WORKOS_API_KEY")
		os.Unsetenv("OPENAI_API_KEY")
		os.Unsetenv("AWS_ACCESS_KEY_ID")
		os.Unsetenv("AWS_SECRET_ACCESS_KEY")
		os.Unsetenv("PORTFOLIO_API_KEY")
		os.Unsetenv("PORTFOLIO_ROOT_ENDPOINT")
	}()

	handlers, err := NewAuthHandlers()
	require.NoError(t, err)

	router := gin.New()
	handlers.SetupRoutes(router)

	t.Run("Login endpoint returns auth URL", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/auth/login", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		
		assert.Contains(t, response, "auth_url")
	})

	t.Run("Callback with invalid JSON fails", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/auth/callback", bytes.NewBufferString("invalid json"))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		
		assert.Contains(t, response, "error")
		assert.Equal(t, "INVALID_REQUEST", response["code"])
	})

	t.Run("Protected route returns 401 without auth", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/v1/me", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Credentials validation endpoint works", func(t *testing.T) {
		creds := clients.AllCredentials{
			OpenAI: struct {
				APIKey string `json:"api_key"`
			}{APIKey: "test-key"},
		}
		body, _ := json.Marshal(creds)
		
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/v1/validate-credentials", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer test-token")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Secrets status endpoint works", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/v1/secrets-status", nil)
		req.Header.Set("Authorization", "Bearer test-token")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		
		assert.Contains(t, response, "secrets")
		secrets := response["secrets"].(map[string]interface{})
		assert.Contains(t, secrets, "openai")
		assert.Contains(t, secrets, "workos")
	})

	t.Run("Logout clears cookie", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/auth/logout", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		cookies := w.Result().Cookies()
		var authCookie *http.Cookie
		for _, cookie := range cookies {
			if cookie.Name == "authToken" {
				authCookie = cookie
				break
			}
		}
		assert.NotNil(t, authCookie)
		assert.Empty(t, authCookie.Value)
		assert.True(t, authCookie.MaxAge < 0)
	})

	t.Run("Public health endpoint works", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest("GET", "/api/public/health", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		
		assert.Equal(t, "healthy", response["status"])
		assert.Equal(t, "consolidated", response["system"])
	})
}