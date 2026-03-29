package testhelpers

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/google/go-cmp/cmp"
	"github.com/matryer/is"
)

// HTTPTestCase represents a single HTTP test case
type HTTPTestCase struct {
	Name           string
	Method         string
	URL            string
	Body           interface{}
	Headers        map[string]string
	ExpectedStatus int
	ExpectedBody   interface{}
	CheckResponse  func(t *testing.T, resp *httptest.ResponseRecorder)
}

// TestRouter creates a Gin router configured for testing
func TestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	return gin.New()
}

// RunHTTPTestCases runs a table of HTTP test cases
func RunHTTPTestCases(t *testing.T, router *gin.Engine, testCases []HTTPTestCase) {
	t.Helper()
	
	for _, tc := range testCases {
		t.Run(tc.Name, func(t *testing.T) {
			is := is.New(t)
			
			// Prepare request body
			var body io.Reader
			if tc.Body != nil {
				bodyBytes, err := json.Marshal(tc.Body)
				is.NoErr(err) // Failed to marshal request body
				body = bytes.NewReader(bodyBytes)
			}
			
			// Create request
			req := httptest.NewRequest(tc.Method, tc.URL, body)
			req.Header.Set("Content-Type", "application/json")
			
			// Add custom headers
			for key, value := range tc.Headers {
				req.Header.Set(key, value)
			}
			
			// Record response
			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)
			
			// Check status code
			is.Equal(w.Code, tc.ExpectedStatus) // Unexpected status code
			
			// Check response body if expected
			if tc.ExpectedBody != nil {
				var actual interface{}
				err := json.Unmarshal(w.Body.Bytes(), &actual)
				is.NoErr(err) // Failed to unmarshal response body
				
				if diff := cmp.Diff(tc.ExpectedBody, actual); diff != "" {
					t.Errorf("Response body mismatch (-want +got):\n%s", diff)
				}
			}
			
			// Run custom response check if provided
			if tc.CheckResponse != nil {
				tc.CheckResponse(t, w)
			}
		})
	}
}

// MakeJSONRequest creates an HTTP request with JSON body
func MakeJSONRequest(method, url string, body interface{}) (*http.Request, error) {
	var bodyReader io.Reader
	
	if body != nil {
		bodyBytes, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewReader(bodyBytes)
	}
	
	req, err := http.NewRequest(method, url, bodyReader)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Content-Type", "application/json")
	return req, nil
}

// ParseJSONResponse parses JSON response into a struct
func ParseJSONResponse(t *testing.T, resp *httptest.ResponseRecorder, target interface{}) {
	t.Helper()
	is := is.New(t)
	
	err := json.Unmarshal(resp.Body.Bytes(), target)
	is.NoErr(err) // Failed to parse JSON response
}

// AssertJSONResponse compares actual JSON response with expected
func AssertJSONResponse(t *testing.T, resp *httptest.ResponseRecorder, expected interface{}) {
	t.Helper()
	
	var actual interface{}
	ParseJSONResponse(t, resp, &actual)
	
	if diff := cmp.Diff(expected, actual); diff != "" {
		t.Errorf("JSON response mismatch (-want +got):\n%s", diff)
	}
}

// AssertErrorResponse checks that the response contains an error with specific message
func AssertErrorResponse(t *testing.T, resp *httptest.ResponseRecorder, expectedMessage string) {
	t.Helper()
	is := is.New(t)
	
	var errorResp struct {
		Error string `json:"error"`
	}
	
	ParseJSONResponse(t, resp, &errorResp)
	is.True(strings.Contains(errorResp.Error, expectedMessage)) // Error message doesn't contain expected text
}

// AssertHeaders checks specific response headers
func AssertHeaders(t *testing.T, resp *httptest.ResponseRecorder, expectedHeaders map[string]string) {
	t.Helper()
	is := is.New(t)
	
	for key, expectedValue := range expectedHeaders {
		actualValue := resp.Header().Get(key)
		is.Equal(actualValue, expectedValue) // Header mismatch for key: %s
	}
}

// CreateAuthenticatedRequest creates a request with mock authentication
func CreateAuthenticatedRequest(method, url string, body interface{}, userID string) (*http.Request, error) {
	req, err := MakeJSONRequest(method, url, body)
	if err != nil {
		return nil, err
	}
	
	// Add mock authentication headers
	req.Header.Set("Authorization", "Bearer mock-token-"+userID)
	req.Header.Set("X-User-ID", userID)
	
	return req, nil
}

// MockWorkOSToken creates a mock WorkOS token for testing
func MockWorkOSToken(userID, email string) string {
	// In real implementation, this would be a proper JWT
	// For testing, we use a simple format that our auth middleware can recognize
	return "mock-workos-token-" + userID + "-" + email
}

// SetupAuthMiddleware creates a mock authentication middleware for testing
func SetupAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}
		
		// Extract user ID from mock token
		if strings.HasPrefix(authHeader, "Bearer mock-token-") {
			userID := strings.TrimPrefix(authHeader, "Bearer mock-token-")
			c.Set("user_id", userID)
			c.Set("authenticated", true)
		} else {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

// CheckJSONStructure validates that response has expected JSON structure
func CheckJSONStructure(t *testing.T, resp *httptest.ResponseRecorder, requiredFields []string) {
	t.Helper()
	is := is.New(t)
	
	var data map[string]interface{}
	ParseJSONResponse(t, resp, &data)
	
	for _, field := range requiredFields {
		_, exists := data[field]
		is.True(exists) // Required field missing: %s
	}
}

// TestWithTimeout wraps test execution with a timeout
func TestWithTimeout(t *testing.T, timeout string, testFunc func()) {
	// For now, just run the test function
	// In the future, this could implement actual timeout logic
	testFunc()
}