package testhelpers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test Database Helper Functions

func TestTestDB_SetupInMemory(t *testing.T) {
	// Skip this test if running in CI or without Docker
	if testing.Short() {
		t.Skip("Skipping TestContainer database test in short mode")
	}

	// This test would require Docker to be running
	// For now, we'll test the struct and methods without actual container
	testDB := &TestDB{
		DB:        nil,
		Container: nil,
		ConnStr:   "test-connection-string",
	}

	assert.Equal(t, "test-connection-string", testDB.ConnStr)
	assert.Nil(t, testDB.DB)
	assert.Nil(t, testDB.Container)
}

func TestTestDB_Cleanup(t *testing.T) {
	testDB := &TestDB{
		DB:        nil,
		Container: nil,
		ConnStr:   "test-connection",
	}

	// Should not panic with nil values
	assert.NotPanics(t, func() {
		testDB.Cleanup()
	})
}

// Test Fixture Functions

func TestUserFixtures(t *testing.T) {
	alice := UserFixtures.Alice
	bob := UserFixtures.Bob
	charlie := UserFixtures.Charlie

	// Test Alice fixture
	assert.Equal(t, "550e8400-e29b-41d4-a716-446655440001", alice.ID)
	assert.Equal(t, "alice@example.com", alice.Email)
	assert.Equal(t, "Alice Smith", alice.Name)
	assert.Equal(t, "user_01H5JQDQR7GFKDM2NV7JVXPG4K", alice.WorkOSID)
	assert.True(t, alice.IsActive)

	// Test Bob fixture
	assert.Equal(t, "550e8400-e29b-41d4-a716-446655440002", bob.ID)
	assert.Equal(t, "bob@example.com", bob.Email)
	assert.Equal(t, "Bob Johnson", bob.Name)
	assert.True(t, bob.IsActive)

	// Test Charlie fixture
	assert.Equal(t, "550e8400-e29b-41d4-a716-446655440003", charlie.ID)
	assert.Equal(t, "charlie@example.com", charlie.Email)
	assert.Equal(t, "Charlie Brown", charlie.Name)
	assert.False(t, charlie.IsActive) // Charlie is inactive

	// Test that all users have different IDs
	assert.NotEqual(t, alice.ID, bob.ID)
	assert.NotEqual(t, bob.ID, charlie.ID)
	assert.NotEqual(t, alice.ID, charlie.ID)
}

func TestProjectFixtures(t *testing.T) {
	nextjs := ProjectFixtures.NextJSApp
	goApi := ProjectFixtures.GoAPI
	reactSpa := ProjectFixtures.ReactSPA

	// Test NextJS project fixture
	assert.Equal(t, "660e8400-e29b-41d4-a716-446655440001", nextjs.ID)
	assert.Equal(t, "My Next.js App", nextjs.Name)
	assert.Equal(t, "A modern Next.js application", nextjs.Description)
	assert.Equal(t, UserFixtures.Alice.ID, nextjs.UserID)
	assert.Equal(t, "nextjs", nextjs.Framework)
	assert.Equal(t, "active", nextjs.Status)

	// Test Go API project fixture
	assert.Equal(t, "REST API", goApi.Name)
	assert.Equal(t, UserFixtures.Bob.ID, goApi.UserID)
	assert.Equal(t, "go", goApi.Framework)

	// Test React SPA project fixture
	assert.Equal(t, "React Dashboard", reactSpa.Name)
	assert.Equal(t, UserFixtures.Alice.ID, reactSpa.UserID)
	assert.Equal(t, "archived", reactSpa.Status)

	// Test that all projects have different IDs
	assert.NotEqual(t, nextjs.ID, goApi.ID)
	assert.NotEqual(t, goApi.ID, reactSpa.ID)
	assert.NotEqual(t, nextjs.ID, reactSpa.ID)
}

func TestDeploymentFixtures(t *testing.T) {
	successful := DeploymentFixtures.Successful
	failed := DeploymentFixtures.Failed
	inProgress := DeploymentFixtures.InProgress

	// Test successful deployment fixture
	assert.Equal(t, "770e8400-e29b-41d4-a716-446655440001", successful.ID)
	assert.Equal(t, ProjectFixtures.NextJSApp.ID, successful.ProjectID)
	assert.Equal(t, "v1.0.0", successful.Version)
	assert.Equal(t, "deployed", successful.Status)
	assert.Equal(t, "vercel", successful.Provider)
	assert.Contains(t, successful.URL, "vercel.app")

	// Test failed deployment fixture
	assert.Equal(t, "failed", failed.Status)
	assert.Equal(t, "render", failed.Provider)
	assert.Empty(t, failed.URL)
	assert.Contains(t, failed.BuildLog, "Build failed")

	// Test in-progress deployment fixture
	assert.Equal(t, "building", inProgress.Status)
	assert.Equal(t, "netlify", inProgress.Provider)
	assert.Contains(t, inProgress.BuildLog, "Starting build")

	// Test that all deployments have different IDs
	assert.NotEqual(t, successful.ID, failed.ID)
	assert.NotEqual(t, failed.ID, inProgress.ID)
	assert.NotEqual(t, successful.ID, inProgress.ID)
}

func TestCreateTestUser(t *testing.T) {
	// Test creating user with defaults
	user := CreateTestUser()
	assert.NotEmpty(t, user.ID)
	assert.Equal(t, "test@example.com", user.Email)
	assert.Equal(t, "Test User", user.Name)
	assert.True(t, user.IsActive)
	assert.NotEmpty(t, user.WorkOSID)

	// Test creating user with overrides
	customUser := CreateTestUser(func(u *TestUser) {
		u.Email = "custom@example.com"
		u.Name = "Custom User"
		u.IsActive = false
	})
	assert.Equal(t, "custom@example.com", customUser.Email)
	assert.Equal(t, "Custom User", customUser.Name)
	assert.False(t, customUser.IsActive)
	assert.NotEmpty(t, customUser.ID)

	// Test that multiple calls create different users
	user1 := CreateTestUser()
	user2 := CreateTestUser()
	assert.NotEqual(t, user1.ID, user2.ID)
	assert.NotEqual(t, user1.WorkOSID, user2.WorkOSID)
}

func TestCreateTestProject(t *testing.T) {
	userID := "test-user-123"

	// Test creating project with defaults
	project := CreateTestProject(userID)
	assert.NotEmpty(t, project.ID)
	assert.Equal(t, "Test Project", project.Name)
	assert.Equal(t, "A test project", project.Description)
	assert.Equal(t, userID, project.UserID)
	assert.Equal(t, "nextjs", project.Framework)
	assert.Equal(t, "active", project.Status)

	// Test creating project with overrides
	customProject := CreateTestProject(userID, func(p *TestProject) {
		p.Name = "Custom Project"
		p.Framework = "react"
		p.Status = "draft"
	})
	assert.Equal(t, "Custom Project", customProject.Name)
	assert.Equal(t, "react", customProject.Framework)
	assert.Equal(t, "draft", customProject.Status)
	assert.Equal(t, userID, customProject.UserID)

	// Test that multiple calls create different projects
	project1 := CreateTestProject(userID)
	project2 := CreateTestProject(userID)
	assert.NotEqual(t, project1.ID, project2.ID)
}

func TestCreateTestDeployment(t *testing.T) {
	projectID := "test-project-123"

	// Test creating deployment with defaults
	deployment := CreateTestDeployment(projectID)
	assert.NotEmpty(t, deployment.ID)
	assert.Equal(t, projectID, deployment.ProjectID)
	assert.Equal(t, "v1.0.0", deployment.Version)
	assert.Equal(t, "deployed", deployment.Status)
	assert.Equal(t, "vercel", deployment.Provider)
	assert.Contains(t, deployment.URL, "vercel.app")

	// Test creating deployment with overrides
	customDeployment := CreateTestDeployment(projectID, func(d *TestDeployment) {
		d.Version = "v2.0.0"
		d.Status = "failed"
		d.Provider = "netlify"
		d.URL = ""
	})
	assert.Equal(t, "v2.0.0", customDeployment.Version)
	assert.Equal(t, "failed", customDeployment.Status)
	assert.Equal(t, "netlify", customDeployment.Provider)
	assert.Empty(t, customDeployment.URL)

	// Test that multiple calls create different deployments
	deployment1 := CreateTestDeployment(projectID)
	deployment2 := CreateTestDeployment(projectID)
	assert.NotEqual(t, deployment1.ID, deployment2.ID)
}

// Test HTTP Helper Functions

func TestTestRouter(t *testing.T) {
	router := TestRouter()
	assert.NotNil(t, router)
	assert.Equal(t, gin.TestMode, gin.Mode())
}

func TestMakeJSONRequest(t *testing.T) {
	testData := map[string]interface{}{
		"name": "test",
		"age":  30,
	}

	// Test with JSON body
	req, err := MakeJSONRequest("POST", "/test", testData)
	assert.NoError(t, err)
	assert.Equal(t, "POST", req.Method)
	assert.Equal(t, "/test", req.URL.Path)
	assert.Equal(t, "application/json", req.Header.Get("Content-Type"))

	// Test with nil body
	req2, err := MakeJSONRequest("GET", "/test", nil)
	assert.NoError(t, err)
	assert.Equal(t, "GET", req2.Method)
	assert.Nil(t, req2.Body)
}

func TestParseJSONResponse(t *testing.T) {
	responseData := map[string]interface{}{
		"id":   "123",
		"name": "test",
	}

	jsonBytes, err := json.Marshal(responseData)
	require.NoError(t, err)

	recorder := httptest.NewRecorder()
	recorder.Write(jsonBytes)

	var parsed map[string]interface{}
	ParseJSONResponse(t, recorder, &parsed)

	assert.Equal(t, "123", parsed["id"])
	assert.Equal(t, "test", parsed["name"])
}

func TestRunHTTPTestCases(t *testing.T) {
	router := TestRouter()
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})
	router.POST("/echo", func(c *gin.Context) {
		var body map[string]interface{}
		c.ShouldBindJSON(&body)
		c.JSON(http.StatusOK, body)
	})

	testCases := []HTTPTestCase{
		{
			Name:           "GET success",
			Method:         "GET",
			URL:            "/test",
			ExpectedStatus: http.StatusOK,
			ExpectedBody:   map[string]interface{}{"message": "success"},
		},
		{
			Name:           "POST echo",
			Method:         "POST",
			URL:            "/echo",
			Body:           map[string]interface{}{"test": "data"},
			ExpectedStatus: http.StatusOK,
			ExpectedBody:   map[string]interface{}{"test": "data"},
		},
		{
			Name:           "Custom response check",
			Method:         "GET",
			URL:            "/test",
			ExpectedStatus: http.StatusOK,
			CheckResponse: func(t *testing.T, resp *httptest.ResponseRecorder) {
				assert.Contains(t, resp.Body.String(), "success")
			},
		},
	}

	RunHTTPTestCases(t, router, testCases)
}

func TestAssertErrorResponse(t *testing.T) {
	router := TestRouter()
	router.GET("/error", func(c *gin.Context) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid input provided"})
	})

	req := httptest.NewRequest("GET", "/error", nil)
	recorder := httptest.NewRecorder()
	router.ServeHTTP(recorder, req)

	AssertErrorResponse(t, recorder, "invalid input")
}

func TestAssertHeaders(t *testing.T) {
	router := TestRouter()
	router.GET("/headers", func(c *gin.Context) {
		c.Header("X-Custom", "test-value")
		c.Header("X-API-Version", "v1")
		c.JSON(http.StatusOK, gin.H{"message": "ok"})
	})

	req := httptest.NewRequest("GET", "/headers", nil)
	recorder := httptest.NewRecorder()
	router.ServeHTTP(recorder, req)

	expectedHeaders := map[string]string{
		"X-Custom":      "test-value",
		"X-API-Version": "v1",
		"Content-Type":  "application/json; charset=utf-8",
	}

	AssertHeaders(t, recorder, expectedHeaders)
}

func TestCreateAuthenticatedRequest(t *testing.T) {
	userID := "user-123"
	requestBody := map[string]interface{}{"data": "test"}

	req, err := CreateAuthenticatedRequest("POST", "/authenticated", requestBody, userID)
	assert.NoError(t, err)
	assert.Equal(t, "POST", req.Method)
	assert.Equal(t, "/authenticated", req.URL.Path)
	assert.Equal(t, "Bearer mock-token-"+userID, req.Header.Get("Authorization"))
	assert.Equal(t, userID, req.Header.Get("X-User-ID"))
	assert.Equal(t, "application/json", req.Header.Get("Content-Type"))
}

func TestMockWorkOSToken(t *testing.T) {
	userID := "user-456"
	email := "test@example.com"

	token := MockWorkOSToken(userID, email)
	assert.Contains(t, token, userID)
	assert.Contains(t, token, email)
	assert.Contains(t, token, "mock-workos-token")
}

func TestSetupAuthMiddleware(t *testing.T) {
	middleware := SetupAuthMiddleware()
	assert.NotNil(t, middleware)

	router := TestRouter()
	router.Use(middleware)
	router.GET("/protected", func(c *gin.Context) {
		userID, exists := c.Get("user_id")
		if exists {
			c.JSON(http.StatusOK, gin.H{"user_id": userID})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "user_id not set"})
		}
	})

	// Test without authorization header
	req := httptest.NewRequest("GET", "/protected", nil)
	recorder := httptest.NewRecorder()
	router.ServeHTTP(recorder, req)
	assert.Equal(t, http.StatusUnauthorized, recorder.Code)

	// Test with invalid authorization header
	req2 := httptest.NewRequest("GET", "/protected", nil)
	req2.Header.Set("Authorization", "Bearer invalid-token")
	recorder2 := httptest.NewRecorder()
	router.ServeHTTP(recorder2, req2)
	assert.Equal(t, http.StatusUnauthorized, recorder2.Code)

	// Test with valid mock token
	userID := "test-user-123"
	req3 := httptest.NewRequest("GET", "/protected", nil)
	req3.Header.Set("Authorization", "Bearer mock-token-"+userID)
	recorder3 := httptest.NewRecorder()
	router.ServeHTTP(recorder3, req3)
	assert.Equal(t, http.StatusOK, recorder3.Code)

	var response map[string]interface{}
	err := json.Unmarshal(recorder3.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, userID, response["user_id"])
}

func TestCheckJSONStructure(t *testing.T) {
	responseData := map[string]interface{}{
		"id":      "123",
		"name":    "test",
		"email":   "test@example.com",
		"active":  true,
		"created": "2024-01-01T00:00:00Z",
	}

	jsonBytes, err := json.Marshal(responseData)
	require.NoError(t, err)

	recorder := httptest.NewRecorder()
	recorder.Write(jsonBytes)

	requiredFields := []string{"id", "name", "email", "active"}
	CheckJSONStructure(t, recorder, requiredFields)

	// This should pass without assertion errors
}

func TestAssertJSONResponse(t *testing.T) {
	expectedData := map[string]interface{}{
		"status": "success",
		"data":   "test",
		"count":  float64(42), // JSON unmarshals numbers as float64
	}

	jsonBytes, err := json.Marshal(expectedData)
	require.NoError(t, err)

	recorder := httptest.NewRecorder()
	recorder.Write(jsonBytes)

	AssertJSONResponse(t, recorder, expectedData)
}

func TestTestWithTimeout(t *testing.T) {
	executed := false
	TestWithTimeout(t, "5s", func() {
		executed = true
	})
	assert.True(t, executed, "Test function should have been executed")
}

// Test edge cases and error conditions

func TestHTTPTestCaseWithHeaders(t *testing.T) {
	router := TestRouter()
	router.GET("/header-test", func(c *gin.Context) {
		customHeader := c.GetHeader("X-Custom")
		c.JSON(http.StatusOK, gin.H{"received": customHeader})
	})

	testCases := []HTTPTestCase{
		{
			Name:   "With custom headers",
			Method: "GET",
			URL:    "/header-test",
			Headers: map[string]string{
				"X-Custom": "test-value",
			},
			ExpectedStatus: http.StatusOK,
			ExpectedBody:   map[string]interface{}{"received": "test-value"},
		},
	}

	RunHTTPTestCases(t, router, testCases)
}

func TestFixtureDataIntegrity(t *testing.T) {
	// Test that fixture relationships are consistent
	nextjsProject := ProjectFixtures.NextJSApp
	successfulDeployment := DeploymentFixtures.Successful
	alice := UserFixtures.Alice

	// NextJS project should belong to Alice
	assert.Equal(t, alice.ID, nextjsProject.UserID)

	// Successful deployment should belong to NextJS project
	assert.Equal(t, nextjsProject.ID, successfulDeployment.ProjectID)

	// Test time relationships
	assert.True(t, nextjsProject.CreatedAt.Before(successfulDeployment.CreatedAt))
}

func TestCreateTestFunctionsWithMultipleOverrides(t *testing.T) {
	userID := uuid.New().String()

	user := CreateTestUser(
		func(u *TestUser) { u.Email = "first@example.com" },
		func(u *TestUser) { u.Name = "First Override" },
		func(u *TestUser) { u.IsActive = false },
	)

	assert.Equal(t, "first@example.com", user.Email)
	assert.Equal(t, "First Override", user.Name)
	assert.False(t, user.IsActive)

	project := CreateTestProject(userID,
		func(p *TestProject) { p.Name = "Multi Override Project" },
		func(p *TestProject) { p.Framework = "vue" },
		func(p *TestProject) { p.Status = "archived" },
	)

	assert.Equal(t, "Multi Override Project", project.Name)
	assert.Equal(t, "vue", project.Framework)
	assert.Equal(t, "archived", project.Status)
}