package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"

	"github.com/byteport/api/models"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

var (
	workosTokenURL    = "https://api.workos.com/sso/token"
	workosUserInfoURL = "https://api.workos.com/user_management/users/me"
	httpPostFunc      = http.Post
	httpDoFunc        = func(req *http.Request) (*http.Response, error) { return http.DefaultClient.Do(req) }
)

// WorkOS AuthKit callback handler
func handleWorkOSCallback(c *gin.Context) {
	var req struct {
		Code  string `json:"code" binding:"required"`
		State string `json:"state"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Exchange code for tokens with WorkOS
	workosClientID := os.Getenv("WORKOS_CLIENT_ID")
	workosClientSecret := os.Getenv("WORKOS_CLIENT_SECRET")

	if workosClientID == "" || workosClientSecret == "" {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "WorkOS not configured"})
		return
	}

	// Exchange authorization code for access token
    tokenReq := map[string]string{
        "client_id":     workosClientID,
        "client_secret": workosClientSecret,
        "code":          req.Code,
        "grant_type":    "authorization_code",
    }

    tokenJSON, _ := json.Marshal(tokenReq)
    resp, err := httpPostFunc(workosTokenURL, "application/json", bytes.NewBuffer(tokenJSON))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to exchange code"})
		return
	}
	defer resp.Body.Close()

	var tokenResp struct {
		AccessToken string `json:"access_token"`
		IdToken     string `json:"id_token"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Invalid token response"})
		return
	}

	// Get user info from WorkOS
    userReq, _ := http.NewRequest("GET", workosUserInfoURL, nil)
    userReq.Header.Set("Authorization", "Bearer "+tokenResp.AccessToken)

    userResp, err := httpDoFunc(userReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user info"})
		return
	}
	defer userResp.Body.Close()

	var userInfo struct {
		ID        string `json:"id"`
		Email     string `json:"email"`
		FirstName string `json:"first_name"`
		LastName  string `json:"last_name"`
	}

	if err := json.NewDecoder(userResp.Body).Decode(&userInfo); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Invalid user info"})
		return
	}

	// Find or create user
	var user models.User
	result := models.DB.Where("email = ?", userInfo.Email).First(&user)

	if result.Error != nil {
		// Create new user
		newUUID := uuid.New()
		user = models.User{
			UUID:  newUUID.String(),
			Name:  userInfo.FirstName + " " + userInfo.LastName,
			Email: userInfo.Email,
		}

		if err := models.DB.Create(&user).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
			return
		}
	}

	// Generate session token (reuse existing JWT system)
	// Note: You may want to replace this with WorkOS session management
	sessionToken := tokenResp.AccessToken // Or generate your own JWT

	// Set auth cookie
	c.SetCookie(
		"authToken",
		sessionToken,
		3600*24*7, // 7 days
		"/",
		"",
		true,  // Secure
		true,  // HttpOnly
	)

	c.JSON(http.StatusOK, gin.H{
		"user":    user,
		"message": "Authentication successful",
	})
}

// Get user by ID
func handleGetUser(c *gin.Context) {
	userID := c.Param("id")

	var user models.User
	if err := models.DB.Where("uuid = ?", userID).First(&user).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, user)
}
