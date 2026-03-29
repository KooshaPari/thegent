package lib

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/byteport/api/models"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupUserTable(t *testing.T, db *gorm.DB) {
	t.Helper()
	err := db.Exec(`CREATE TABLE IF NOT EXISTS users (
        uuid TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        aws_access_key_id TEXT DEFAULT '',
        aws_secret_access_key TEXT DEFAULT '',
        llm_provider TEXT DEFAULT '',
        llm_providers TEXT DEFAULT '{}',
        portfolio_root_endpoint TEXT DEFAULT '',
        portfolio_api_key TEXT DEFAULT '',
        created_at DATETIME,
        updated_at DATETIME
    )`).Error
	require.NoError(t, err)
}

func TestInitAuthSystem(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	err := InitAuthSystem()
	assert.NoError(t, err)

	_, err = keyringGet(tokenKeyService, keyringUser)
	assert.NoError(t, err)

	_, err = keyringGet(secretsKeyService, keyringUser)
	assert.NoError(t, err)

	_, err = keyringGet(serviceKeyService, keyringUser)
	assert.NoError(t, err)

	serviceKey := os.Getenv("SERVICE_KEY")
	assert.NotEmpty(t, serviceKey)
}

func TestEnsureKeyExists(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()

	service := "test-service"
	user := "test-user"

	err := ensureKeyExists(service, user)
	assert.NoError(t, err)

	key1, err := keyringGet(service, user)
	assert.NoError(t, err)
	assert.NotEmpty(t, key1)

	err = ensureKeyExists(service, user)
	assert.NoError(t, err)

	key2, err := keyringGet(service, user)
	assert.NoError(t, err)
	assert.Equal(t, key1, key2)
}

func TestGenerateSymmetricKey(t *testing.T) {
	key := generateSymmetricKey()
	assert.NotEmpty(t, key)
	assert.Equal(t, 64, len(key))
	key2 := generateSymmetricKey()
	assert.NotEqual(t, key, key2)
}

func TestGetSymmetricKey(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()

	err := ensureKeyExists(tokenKeyService, keyringUser)
	require.NoError(t, err)

	key, err := getSymmetricKey()
	assert.NoError(t, err)
	assert.NotEmpty(t, key)
}

func TestGenerateToken(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)
	models.DB = db
	setupUserTable(t, db)

	err = InitAuthSystem()
	require.NoError(t, err)

	user := models.User{UUID: "test-user-123", Email: "test@example.com"}

	token, err := GenerateToken(user)
	assert.NoError(t, err)
	assert.NotEmpty(t, token)

	valid, parsedToken, err := ValidateToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)
	assert.NotNil(t, parsedToken)
}

func TestGenerateNVMSToken(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	err := InitAuthSystem()
	require.NoError(t, err)

	project := models.Project{
		UUID: "test-project-123",
		User: models.User{UUID: "test-user-123"},
	}

	token, err := GenerateNVMSToken(project)
	assert.NoError(t, err)
	assert.NotEmpty(t, token)

	valid, _, err := ValidateServiceToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)
}

func TestValidateToken(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	err := InitAuthSystem()
	require.NoError(t, err)

	user := models.User{UUID: "test-user-123", Email: "test@example.com"}
	token, err := GenerateToken(user)
	require.NoError(t, err)

	valid, parsedToken, err := ValidateToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)
	assert.NotNil(t, parsedToken)

	valid, parsedToken, err = ValidateToken("invalid-token")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, parsedToken)
}

func TestValidateServiceToken(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	err := InitAuthSystem()
	require.NoError(t, err)

	project := models.Project{UUID: "test-project-123", User: models.User{UUID: "test-user-123"}}
	token, err := GenerateNVMSToken(project)
	require.NoError(t, err)

	valid, _, err := ValidateServiceToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)

	valid, parsedToken, err := ValidateServiceToken("invalid-token")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, parsedToken)
}

func TestAuthenticateRequest(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)
	models.DB = db
	setupUserTable(t, db)

	err = InitAuthSystem()
	require.NoError(t, err)

	err = db.Exec(`INSERT INTO users (uuid, name, email, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)`,
		"test-user-123", "", "test@example.com", "hashed-password", time.Now(), time.Now()).Error
	require.NoError(t, err)

	user := models.User{UUID: "test-user-123", Email: "test@example.com", Password: "hashed"}
	token, err := GenerateToken(user)
	require.NoError(t, err)

	authenticatedUser, err := AuthenticateRequest(token)
	assert.NoError(t, err)
	assert.NotNil(t, authenticatedUser)

	authenticatedUser, err = AuthenticateRequest("invalid-token")
	assert.Error(t, err)
	assert.Nil(t, authenticatedUser)
}

func TestAuthMiddleware(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)
	models.DB = db
	setupUserTable(t, db)

	err = InitAuthSystem()
	require.NoError(t, err)

	err = db.Exec(`INSERT INTO users (uuid, name, email, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)`,
		"test-user-123", "", "test@example.com", "hashed-password", time.Now(), time.Now()).Error
	require.NoError(t, err)

	user := models.User{UUID: "test-user-123", Email: "test@example.com"}
	token, err := GenerateToken(user)
	require.NoError(t, err)

	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.Use(AuthMiddleware())
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	req := httptest.NewRequest(http.MethodGet, "/protected", nil)
	req.AddCookie(&http.Cookie{Name: "authToken", Value: token})
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)

	req = httptest.NewRequest(http.MethodGet, "/protected", nil)
	w = httptest.NewRecorder()
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}
