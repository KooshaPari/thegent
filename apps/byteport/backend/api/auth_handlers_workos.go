package main

import (
	"context"
	"net/http"
	"os"
	"time"

	"github.com/byteport/api/internal/infrastructure/auth"
	"github.com/byteport/api/internal/infrastructure/clients"
	"github.com/byteport/api/internal/infrastructure/secrets"
	"github.com/byteport/api/models"
	"github.com/gin-gonic/gin"
)

// AuthHandlers provides modern authentication handlers using WorkOS and production secrets management
type AuthHandlers struct {
	workosAuth       *auth.WorkOSAuthService
	secretsManager   *secrets.Manager
	credValidator    *clients.CredentialValidator
}

// NewAuthHandlers creates a new instance with all dependencies
func NewAuthHandlers() (*AuthHandlers, error) {
	// Initialize production secrets management
	secretsManager := secrets.New(secrets.Config{
		CacheTTL: 5 * time.Minute,
	})
	
	// Register providers in order of preference
	// Try AWS Secrets Manager first if available
	if awsProvider, err := secrets.NewAWSSecretsProvider(context.Background(), "us-east-1"); err == nil {
		secretsManager.RegisterProvider("aws", awsProvider)
	}
	
	// Try Vault if available
	if vaultAddr := os.Getenv("VAULT_ADDR"); vaultAddr != "" {
		if vaultToken := os.Getenv("VAULT_TOKEN"); vaultToken != "" {
			if vaultProvider, err := secrets.NewVaultProvider(vaultAddr, vaultToken, "secret"); err == nil {
				secretsManager.RegisterProvider("vault", vaultProvider)
			}
		}
	}
	
	// Always register environment provider as fallback
	secretsManager.RegisterProvider("env", secrets.NewEnvironmentProvider())

	// Initialize WorkOS authentication
	workosAuth := auth.NewWorkOSAuthService(secretsManager)
	if err := workosAuth.Initialize(context.Background()); err != nil {
		return nil, err
	}

	// Initialize credential validator
	credValidator := clients.NewCredentialValidator()

	return &AuthHandlers{
		workosAuth:     workosAuth,
		secretsManager: secretsManager,
		credValidator:  credValidator,
	}, nil
}

// HandleAuthLogin generates a WorkOS authorization URL
func (h *AuthHandlers) HandleAuthLogin(c *gin.Context) {
	authURL, err := h.workosAuth.GetAuthURL(c.Request.Context(), "byteport-auth-state")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to generate auth URL",
			"code":  "AUTH_URL_ERROR",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"auth_url": authURL,
		"message":  "Redirect to this URL to authenticate with WorkOS",
	})
}

// HandleAuthCallback processes the WorkOS OAuth callback
func (h *AuthHandlers) HandleAuthCallback(c *gin.Context) {
	var req models.WorkOSAuthRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request format",
			"code":  "INVALID_REQUEST",
		})
		return
	}

	// Exchange code for tokens
	tokenResp, err := h.workosAuth.ExchangeCodeForToken(c.Request.Context(), req.Code)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to exchange authorization code",
			"code":  "TOKEN_EXCHANGE_ERROR",
		})
		return
	}

	// Validate token and get user info
	userInfo, err := h.workosAuth.ValidateToken(c.Request.Context(), tokenResp.AccessToken)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to validate token",
			"code":  "TOKEN_VALIDATION_ERROR",
		})
		return
	}

	// Find or create user in our database
	workosUserInfo := &models.WorkOSUserInfo{
		ID:        userInfo.ID,
		Email:     userInfo.Email,
		FirstName: userInfo.FirstName,
		LastName:  userInfo.LastName,
	}

	user, err := models.FindOrCreateUserFromWorkOS(workosUserInfo)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create/update user",
			"code":  "USER_CREATION_ERROR",
		})
		return
	}

	// Set auth cookie with WorkOS access token
	c.SetCookie(
		"authToken",
		tokenResp.AccessToken,
		int(tokenResp.ExpiresIn), // Use actual token expiration
		"/",
		"",
		true,  // Secure
		true,  // HttpOnly
	)

	c.JSON(http.StatusOK, gin.H{
		"user":    user,
		"message": "Authentication successful",
		"system":  "workos",
	})
}

// HandleMe returns the current authenticated user
func (h *AuthHandlers) HandleMe(c *gin.Context) {
	userInfo, exists := c.Get("user_info")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "User not authenticated",
			"code":  "NOT_AUTHENTICATED",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user": userInfo,
	})
}

// HandleValidateCredentials validates external service credentials using official SDKs
func (h *AuthHandlers) HandleValidateCredentials(c *gin.Context) {
	var creds clients.AllCredentials
	if err := c.ShouldBindJSON(&creds); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid credentials format",
			"code":  "INVALID_CREDENTIALS",
		})
		return
	}

	// Validate all credentials using official SDKs
	results := h.credValidator.ValidateAllCredentials(c.Request.Context(), &creds)

	c.JSON(http.StatusOK, gin.H{
		"validation_results": results,
		"timestamp":          gin.H{"validated_at": "now"},
	})
}

// HandleGetSecrets returns configured secrets (for admin/debug purposes)
func (h *AuthHandlers) HandleGetSecrets(c *gin.Context) {
	ctx := c.Request.Context()
	
	secretsInfo := gin.H{}

	// Check which secrets are configured (without revealing values)
	if apiKey, err := h.secretsManager.GetOpenAIConfig(ctx); err == nil && apiKey != "" {
		secretsInfo["openai"] = "configured"
	}

	if accessKey, secretKey, region, err := h.secretsManager.GetAWSConfig(ctx); err == nil && accessKey != "" && secretKey != "" {
		secretsInfo["aws"] = gin.H{
			"configured": true,
			"region":     region,
		}
	}

	if apiKey, endpoint, err := h.secretsManager.GetPortfolioConfig(ctx); err == nil && apiKey != "" && endpoint != "" {
		secretsInfo["portfolio"] = "configured"
	}

	if clientID, _, apiKey, err := h.secretsManager.GetWorkOSConfig(ctx); err == nil && clientID != "" && apiKey != "" {
		secretsInfo["workos"] = "configured"
	}

	c.JSON(http.StatusOK, gin.H{
		"secrets": secretsInfo,
		"message": "Secrets configuration status",
	})
}

// HandleLogout clears the authentication cookie
func (h *AuthHandlers) HandleLogout(c *gin.Context) {
	c.SetCookie(
		"authToken",
		"",
		-1, // Expire immediately
		"/",
		"",
		true,  // Secure
		true,  // HttpOnly
	)

	c.JSON(http.StatusOK, gin.H{
		"message": "Logged out successfully",
	})
}

// SetupRoutes configures routes using the modern authentication system
func (h *AuthHandlers) SetupRoutes(router *gin.Engine) {
	// Public authentication routes
	auth := router.Group("/auth")
	{
		auth.GET("/login", h.HandleAuthLogin)
		auth.POST("/callback", h.HandleAuthCallback)
		auth.POST("/logout", h.HandleLogout)
	}

	// Protected API routes
	api := router.Group("/api/v1")
	api.Use(h.workosAuth.Middleware()) // Use WorkOS middleware for authentication
	{
		api.GET("/me", h.HandleMe)
		api.POST("/validate-credentials", h.HandleValidateCredentials)
		api.GET("/secrets-status", h.HandleGetSecrets)
	}

	// Optional authentication routes (enhanced if authenticated)
	public := router.Group("/api/public")
	public.Use(h.workosAuth.OptionalMiddleware())
	{
		public.GET("/health", func(c *gin.Context) {
			userInfo, authenticated := c.Get("user_info")
			
			health := gin.H{
				"status": "healthy",
				"system": "consolidated",
			}

			if authenticated {
				health["authenticated_user"] = userInfo
			}

			c.JSON(http.StatusOK, health)
		})
	}
}

// Example of how to use this in main server setup:
/*
func setupAuth(router *gin.Engine) error {
	handlers, err := NewAuthHandlers()
	if err != nil {
		return fmt.Errorf("failed to initialize auth handlers: %w", err)
	}

	handlers.SetupRoutes(router)
	return nil
}
*/
