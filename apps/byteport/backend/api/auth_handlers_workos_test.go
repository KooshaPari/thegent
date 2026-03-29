package main

import (
    "bytes"
    "context"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "os"
    "testing"
    "time"

    "github.com/byteport/api/internal/infrastructure/auth"
    "github.com/byteport/api/internal/infrastructure/clients"
    "github.com/byteport/api/internal/infrastructure/secrets"
    "github.com/byteport/api/models"
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

type mockOpenAIClient struct {
    err error
}

func (m *mockOpenAIClient) ListModels(ctx context.Context) (openaiModelsList, error) {
    return openaiModelsList{}, m.err
}

type openaiModelsList struct{}

var _ clients.OpenAIModelLister = (*mockOpenAIClient)(nil)

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) { return f(req) }

func setupWorkOSAuthHandlers(t *testing.T) *AuthHandlers {
    t.Helper()

    os.Setenv("WORKOS_CLIENT_ID", "test-client-id")
    os.Setenv("WORKOS_CLIENT_SECRET", "test-client-secret")
    os.Setenv("WORKOS_API_KEY", "test-api-key")
    t.Cleanup(func() {
        os.Unsetenv("WORKOS_CLIENT_ID")
        os.Unsetenv("WORKOS_CLIENT_SECRET")
        os.Unsetenv("WORKOS_API_KEY")
    })

    secretsManager := secrets.New(secrets.Config{CacheTTL: time.Minute})
    secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())

    workosService := auth.NewWorkOSAuthService(secretsManager)
    require.NoError(t, workosService.Initialize(context.Background()))

    mockOpenAI := &mockOpenAIClient{}
    httpClient := &http.Client{Transport: roundTripFunc(func(req *http.Request) (*http.Response, error) {
        return &http.Response{StatusCode: http.StatusOK, Body: http.NoBody, Header: make(http.Header)}, nil
    })}

    validator := clients.NewCredentialValidator(
        clients.WithHTTPClient(httpClient),
        clients.WithOpenAIClientFactory(func(apiKey string) clients.OpenAIModelLister { return mockOpenAI }),
    )

    return &AuthHandlers{
        workosAuth:     workosService,
        secretsManager: secretsManager,
        credValidator:  validator,
    }
}

func setupWorkOSDB(t *testing.T) {
    t.Helper()
    db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
    require.NoError(t, err)
    require.NoError(t, db.AutoMigrate(&models.WorkOSUser{}, &models.User{}))
    models.DB = db
}

func TestHandleAuthLogin(t *testing.T) {
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    w := httptest.NewRecorder()
    c, router := gin.CreateTestContext(w)
    c.Request = httptest.NewRequest(http.MethodGet, "/auth/login", nil)

    router.GET("/auth/login", handler.HandleAuthLogin)
    router.ServeHTTP(w, c.Request)

    assert.Equal(t, http.StatusOK, w.Code)
    assert.Contains(t, w.Body.String(), "auth_url")

    // Error path with uninitialized client
    errorHandler := &AuthHandlers{workosAuth: &auth.WorkOSAuthService{}}
    w = httptest.NewRecorder()
    router = gin.New()
    router.GET("/auth/login", errorHandler.HandleAuthLogin)
    router.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/auth/login", nil))
    assert.Equal(t, http.StatusInternalServerError, w.Code)
}

func TestHandleAuthCallback(t *testing.T) {
    setupWorkOSDB(t)
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    router := gin.New()
    router.POST("/auth/callback", handler.HandleAuthCallback)

    payload := map[string]string{"code": "test-user123-john_at_example.com"}
    body, _ := json.Marshal(payload)
    req := httptest.NewRequest(http.MethodPost, "/auth/callback", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusOK, w.Code)
    assert.NotEmpty(t, w.Result().Cookies())

    // invalid JSON
    w = httptest.NewRecorder()
    router.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/auth/callback", bytes.NewReader([]byte("invalid"))))
    assert.Equal(t, http.StatusBadRequest, w.Code)

    // empty code triggers error
    payload = map[string]string{"code": ""}
    body, _ = json.Marshal(payload)
    w = httptest.NewRecorder()
    req = httptest.NewRequest(http.MethodPost, "/auth/callback", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusInternalServerError, w.Code)
}

func TestHandleMe(t *testing.T) {
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    c, _ := gin.CreateTestContext(httptest.NewRecorder())
    handler.HandleMe(c)
    assert.Equal(t, http.StatusUnauthorized, c.Writer.Status())

    w := httptest.NewRecorder()
    c, _ = gin.CreateTestContext(w)
    c.Set("user_info", map[string]string{"id": "123"})
    handler.HandleMe(c)
    assert.Equal(t, http.StatusOK, w.Code)
}

func TestHandleValidateCredentials(t *testing.T) {
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    router := gin.New()
    router.POST("/validate", handler.HandleValidateCredentials)

    creds := map[string]interface{}{
        "openai": map[string]string{"api_key": "sk-test"},
        "portfolio": map[string]string{"endpoint": "https://portfolio.example.com", "api_key": "secret"},
    }
    body, _ := json.Marshal(creds)
    req := httptest.NewRequest(http.MethodPost, "/validate", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusOK, w.Code)
}

func TestHandleGetSecrets(t *testing.T) {
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    router := gin.New()
    router.GET("/secrets", handler.HandleGetSecrets)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/secrets", nil))
    assert.Equal(t, http.StatusOK, w.Code)
}

func TestHandleLogout(t *testing.T) {
    handler := setupWorkOSAuthHandlers(t)

    gin.SetMode(gin.TestMode)
    router := gin.New()
    router.POST("/logout", handler.HandleLogout)

    w := httptest.NewRecorder()
    router.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/logout", nil))
    assert.Equal(t, http.StatusOK, w.Code)
}

func TestHandleWorkOSCallback(t *testing.T) {
    setupWorkOSDB(t)

    tokenServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        switch r.URL.Path {
        case "/sso/token":
            json.NewEncoder(w).Encode(map[string]string{
                "access_token": "test-access",
                "id_token":     "id",
            })
        case "/user_management/users/me":
            json.NewEncoder(w).Encode(map[string]string{
                "id":         "user-1",
                "email":      "user@example.com",
                "first_name": "Unit",
                "last_name":  "Test",
            })
        default:
            w.WriteHeader(http.StatusNotFound)
        }
    }))
    defer tokenServer.Close()

    oldTokenURL, oldUserURL, oldPost, oldDo := workosTokenURL, workosUserInfoURL, httpPostFunc, httpDoFunc
    workosTokenURL = tokenServer.URL + "/sso/token"
    workosUserInfoURL = tokenServer.URL + "/user_management/users/me"
    httpPostFunc = func(url, contentType string, body *bytes.Buffer) (*http.Response, error) {
        return http.Post(url, contentType, body)
    }
    httpDoFunc = func(req *http.Request) (*http.Response, error) {
        client := &http.Client{}
        return client.Do(req)
    }
    os.Setenv("WORKOS_CLIENT_ID", "id")
    os.Setenv("WORKOS_CLIENT_SECRET", "secret")
    t.Cleanup(func() {
        workosTokenURL, workosUserInfoURL = oldTokenURL, oldUserURL
        httpPostFunc, httpDoFunc = oldPost, oldDo
        os.Unsetenv("WORKOS_CLIENT_ID")
        os.Unsetenv("WORKOS_CLIENT_SECRET")
    })

    gin.SetMode(gin.TestMode)
    router := gin.New()
    router.POST("/callback", handleWorkOSCallback)

    payload := map[string]string{"code": "test-code"}
    body, _ := json.Marshal(payload)
    w := httptest.NewRecorder()
    req := httptest.NewRequest(http.MethodPost, "/callback", bytes.NewReader(mustBuffer(body)))
    req.Header.Set("Content-Type", "application/json")
    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusOK, w.Code)
}

func mustBuffer(b []byte) []byte {
    return b
}
