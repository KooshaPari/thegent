package handlers

import (
	"byteport/api/models"
	"byteport/api/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

// getUser retrieves the authenticated user from Gin context.
// In production this is populated by the auth middleware.
func getUser(c *gin.Context) *models.User {
	val, exists := c.Get("user")
	if !exists {
		return nil
	}
	user, ok := val.(*models.User)
	if !ok {
		return nil
	}
	return user
}

func unauthorizedToken(c *gin.Context, provider string) {
	c.JSON(http.StatusUnauthorized, gin.H{"error": provider + " token not configured"})
}

// RegisterProviderRoutes attaches all provider routes to the given router group.
func RegisterProviderRoutes(rg *gin.RouterGroup) {
	v := rg.Group("/providers")

	// Vercel
	v.GET("/vercel/projects", HandleVercelProjects)
	v.GET("/vercel/deployments", HandleVercelDeployments)

	// Netlify
	v.GET("/netlify/sites", HandleNetlifySites)
	v.GET("/netlify/sites/:siteId/deploys", HandleNetlifyDeploys)

	// Railway
	v.GET("/railway/projects", HandleRailwayProjects)
	v.POST("/railway/deploy", HandleRailwayDeploy)

	// Fly.io
	v.GET("/flyio/apps", HandleFlyioApps)
	v.GET("/flyio/apps/:appName/machines", HandleFlyioMachines)

	// Supabase
	v.GET("/supabase/projects", HandleSupabaseProjects)
}

// HandleVercelProjects godoc
// GET /api/providers/vercel/projects
func HandleVercelProjects(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.VercelCreds == nil || user.VercelCreds.Token == "" {
		unauthorizedToken(c, "Vercel")
		return
	}
	client := services.NewVercelClient(user.VercelCreds.Token)
	projects, err := client.ListProjects()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, projects)
}

// HandleVercelDeployments godoc
// GET /api/providers/vercel/deployments?projectId=<id>
func HandleVercelDeployments(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.VercelCreds == nil || user.VercelCreds.Token == "" {
		unauthorizedToken(c, "Vercel")
		return
	}
	projectID := c.Query("projectId")
	client := services.NewVercelClient(user.VercelCreds.Token)
	deployments, err := client.ListDeployments(projectID)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, deployments)
}

// HandleNetlifySites godoc
// GET /api/providers/netlify/sites
func HandleNetlifySites(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.NetlifyCreds == nil || user.NetlifyCreds.Token == "" {
		unauthorizedToken(c, "Netlify")
		return
	}
	client := services.NewNetlifyClient(user.NetlifyCreds.Token)
	sites, err := client.ListSites()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, sites)
}

// HandleNetlifyDeploys godoc
// GET /api/providers/netlify/sites/:siteId/deploys
func HandleNetlifyDeploys(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.NetlifyCreds == nil || user.NetlifyCreds.Token == "" {
		unauthorizedToken(c, "Netlify")
		return
	}
	siteID := c.Param("siteId")
	client := services.NewNetlifyClient(user.NetlifyCreds.Token)
	deploys, err := client.ListDeploys(siteID)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, deploys)
}

// HandleRailwayProjects godoc
// GET /api/providers/railway/projects
func HandleRailwayProjects(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.RailwayCreds == nil || user.RailwayCreds.Token == "" {
		unauthorizedToken(c, "Railway")
		return
	}
	client := services.NewRailwayClient(user.RailwayCreds.Token)
	projects, err := client.ListProjects()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, projects)
}

// HandleRailwayDeploy godoc
// POST /api/providers/railway/deploy
// Body: { "serviceId": "...", "environmentId": "..." }
func HandleRailwayDeploy(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.RailwayCreds == nil || user.RailwayCreds.Token == "" {
		unauthorizedToken(c, "Railway")
		return
	}
	var body struct {
		ServiceID     string `json:"serviceId" binding:"required"`
		EnvironmentID string `json:"environmentId" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	client := services.NewRailwayClient(user.RailwayCreds.Token)
	if err := client.TriggerDeploy(body.ServiceID, body.EnvironmentID); err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "deploy triggered"})
}

// HandleFlyioApps godoc
// GET /api/providers/flyio/apps
func HandleFlyioApps(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.FlyIOCreds == nil || user.FlyIOCreds.Token == "" {
		unauthorizedToken(c, "Fly.io")
		return
	}
	client := services.NewFlyioClient(user.FlyIOCreds.Token)
	apps, err := client.ListApps()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, apps)
}

// HandleFlyioMachines godoc
// GET /api/providers/flyio/apps/:appName/machines
func HandleFlyioMachines(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.FlyIOCreds == nil || user.FlyIOCreds.Token == "" {
		unauthorizedToken(c, "Fly.io")
		return
	}
	appName := c.Param("appName")
	client := services.NewFlyioClient(user.FlyIOCreds.Token)
	machines, err := client.ListMachines(appName)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, machines)
}

// HandleSupabaseProjects godoc
// GET /api/providers/supabase/projects
func HandleSupabaseProjects(c *gin.Context) {
	user := getUser(c)
	if user == nil || user.SupabaseCreds == nil || user.SupabaseCreds.Token == "" {
		unauthorizedToken(c, "Supabase")
		return
	}
	client := services.NewSupabaseClient(user.SupabaseCreds.Token)
	projects, err := client.ListProjects()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, projects)
}
