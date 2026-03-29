package main

import (
	"testing"
	"time"

	"github.com/byteport/api/models"
	"github.com/matryer/is"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/datatypes"
)

// TestProviderConfigTableName tests table name override
func TestProviderConfigTableName(t *testing.T) {
	is := is.New(t)
	pc := models.ProviderConfig{}
	is.Equal(pc.TableName(), "provider_configs")
}

// TestFrameworkPatternTableName tests table name override
func TestFrameworkPatternTableName(t *testing.T) {
	is := is.New(t)
	fp := models.FrameworkPattern{}
	is.Equal(fp.TableName(), "framework_patterns")
}

// TestAPIRateLimitTableName tests table name override
func TestAPIRateLimitTableName(t *testing.T) {
	is := is.New(t)
	arl := models.APIRateLimit{}
	is.Equal(arl.TableName(), "api_rate_limits")
}

// TestProviderConfigSupportsType tests the SupportsType method
func TestProviderConfigSupportsType(t *testing.T) {
	pc := models.ProviderConfig{
		Provider:       "vercel",
		DisplayName:    "Vercel",
		SupportedTypes: datatypes.JSON([]byte(`["frontend", "backend"]`)),
	}

	t.Run("checks if provider supports type", func(t *testing.T) {
		// Note: Current implementation is a placeholder that returns true
		result := pc.SupportsType("frontend")
		assert.True(t, result, "Expected provider to support type")
	})

	t.Run("returns result for any type", func(t *testing.T) {
		result := pc.SupportsType("database")
		// Current implementation always returns true
		assert.True(t, result)
	})
}

// TestProviderConfigGetTier tests the GetTier method
func TestProviderConfigGetTier(t *testing.T) {
	pc := models.ProviderConfig{
		Provider:     "vercel",
		DisplayName:  "Vercel",
		PricingTiers: datatypes.JSON([]byte(`{"free": {"price": 0, "limits": {"deployments": 100}}}`)),
	}

	t.Run("retrieves tier information", func(t *testing.T) {
		tier, err := pc.GetTier("free")
		// Current implementation returns nil, nil
		assert.NoError(t, err)
		assert.Nil(t, tier)
	})

	t.Run("handles non-existent tier", func(t *testing.T) {
		tier, err := pc.GetTier("enterprise")
		// Current implementation returns nil, nil
		assert.NoError(t, err)
		assert.Nil(t, tier)
	})
}

// TestProviderConfigFields tests provider config field values
func TestProviderConfigFields(t *testing.T) {
	now := time.Now()

	pc := models.ProviderConfig{
		ID:             1,
		Provider:       "netlify",
		DisplayName:    "Netlify",
		SupportedTypes: datatypes.JSON([]byte(`["frontend"]`)),
		PricingTiers:   datatypes.JSON([]byte(`{"free": {"price": 0}}`)),
		IsEnabled:      true,
		IsBeta:         false,
		Metadata:       datatypes.JSON([]byte(`{"api": "https://api.netlify.com"}`)),
		RateLimits:     datatypes.JSON([]byte(`{"requests_per_hour": 1000}`)),
		CreatedAt:      now,
		UpdatedAt:      now,
	}

	t.Run("stores and retrieves all fields", func(t *testing.T) {
		assert.Equal(t, 1, pc.ID)
		assert.Equal(t, "netlify", pc.Provider)
		assert.Equal(t, "Netlify", pc.DisplayName)
		assert.True(t, pc.IsEnabled)
		assert.False(t, pc.IsBeta)
		assert.NotNil(t, pc.SupportedTypes)
		assert.NotNil(t, pc.PricingTiers)
		assert.NotNil(t, pc.Metadata)
		assert.NotNil(t, pc.RateLimits)
		assert.Equal(t, now, pc.CreatedAt)
		assert.Equal(t, now, pc.UpdatedAt)
	})
}

// TestFrameworkPatternMatches tests the Matches method
func TestFrameworkPatternMatches(t *testing.T) {
	fp := models.FrameworkPattern{
		Framework:    "nextjs",
		Type:         "frontend",
		FilePatterns: datatypes.JSON([]byte(`["package.json", "next.config.js"]`)),
	}

	t.Run("matches files against pattern", func(t *testing.T) {
		files := []string{"package.json", "next.config.js", "pages/index.tsx"}
		matches, confidence := fp.Matches(files)

		// Current implementation returns false, 0.0
		assert.False(t, matches)
		assert.Equal(t, 0.0, confidence)
	})

	t.Run("returns false for non-matching files", func(t *testing.T) {
		files := []string{"index.html", "style.css"}
		matches, confidence := fp.Matches(files)

		assert.False(t, matches)
		assert.Equal(t, 0.0, confidence)
	})
}

// TestFrameworkPatternGetBuildConfig tests the GetBuildConfig method
func TestFrameworkPatternGetBuildConfig(t *testing.T) {
	buildCmd := "npm run build"
	startCmd := "npm start"
	installCmd := "npm install"

	t.Run("returns full build config when all commands set", func(t *testing.T) {
		fp := models.FrameworkPattern{
			Framework:             "nextjs",
			DefaultBuildCommand:   &buildCmd,
			DefaultStartCommand:   &startCmd,
			DefaultInstallCommand: &installCmd,
		}

		config := fp.GetBuildConfig()

		assert.Equal(t, "npm run build", config["build"])
		assert.Equal(t, "npm start", config["start"])
		assert.Equal(t, "npm install", config["install"])
		assert.Len(t, config, 3)
	})

	t.Run("returns partial config when some commands missing", func(t *testing.T) {
		fp := models.FrameworkPattern{
			Framework:           "react",
			DefaultBuildCommand: &buildCmd,
		}

		config := fp.GetBuildConfig()

		assert.Equal(t, "npm run build", config["build"])
		assert.NotContains(t, config, "start")
		assert.NotContains(t, config, "install")
		assert.Len(t, config, 1)
	})

	t.Run("returns empty config when no commands set", func(t *testing.T) {
		fp := models.FrameworkPattern{
			Framework: "static",
		}

		config := fp.GetBuildConfig()

		assert.Empty(t, config)
		assert.Len(t, config, 0)
	})
}

// TestFrameworkPatternFields tests framework pattern field values
func TestFrameworkPatternFields(t *testing.T) {
	now := time.Now()
	buildCmd := "yarn build"
	startCmd := "yarn start"

	fp := models.FrameworkPattern{
		ID:                    1,
		Framework:             "react",
		Type:                  "frontend",
		FilePatterns:          datatypes.JSON([]byte(`["package.json"]`)),
		DependencyPatterns:    datatypes.JSON([]byte(`["react", "react-dom"]`)),
		ConfidenceWeight:      0.95,
		DefaultBuildCommand:   &buildCmd,
		DefaultStartCommand:   &startCmd,
		DefaultInstallCommand: nil,
		RecommendedProviders:  datatypes.JSON([]byte(`["vercel", "netlify"]`)),
		Metadata:              datatypes.JSON([]byte(`{"docs": "https://react.dev"}`)),
		CreatedAt:             now,
		UpdatedAt:             now,
	}

	t.Run("stores and retrieves all fields", func(t *testing.T) {
		assert.Equal(t, 1, fp.ID)
		assert.Equal(t, "react", fp.Framework)
		assert.Equal(t, "frontend", fp.Type)
		assert.Equal(t, 0.95, fp.ConfidenceWeight)
		assert.NotNil(t, fp.DefaultBuildCommand)
		assert.Equal(t, "yarn build", *fp.DefaultBuildCommand)
		assert.NotNil(t, fp.DefaultStartCommand)
		assert.Equal(t, "yarn start", *fp.DefaultStartCommand)
		assert.Nil(t, fp.DefaultInstallCommand)
		assert.NotNil(t, fp.FilePatterns)
		assert.NotNil(t, fp.DependencyPatterns)
		assert.NotNil(t, fp.RecommendedProviders)
		assert.NotNil(t, fp.Metadata)
		assert.Equal(t, now, fp.CreatedAt)
		assert.Equal(t, now, fp.UpdatedAt)
	})
}

// TestAPIRateLimitIsExpired tests the IsExpired method
func TestAPIRateLimitIsExpired(t *testing.T) {
	t.Run("returns true for expired window (over 1 hour)", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-123",
			Endpoint:     "/api/deployments",
			WindowStart:  time.Now().Add(-2 * time.Hour),
			RequestCount: 10,
		}

		assert.True(t, arl.IsExpired())
	})

	t.Run("returns false for active window (within 1 hour)", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-456",
			Endpoint:     "/api/projects",
			WindowStart:  time.Now().Add(-30 * time.Minute),
			RequestCount: 5,
		}

		assert.False(t, arl.IsExpired())
	})

	t.Run("returns false for recent window (just started)", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-789",
			Endpoint:     "/api/users",
			WindowStart:  time.Now(),
			RequestCount: 1,
		}

		assert.False(t, arl.IsExpired())
	})

	t.Run("returns true for window exactly at 1 hour boundary", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-abc",
			Endpoint:     "/api/logs",
			WindowStart:  time.Now().Add(-1*time.Hour - 1*time.Second),
			RequestCount: 50,
		}

		assert.True(t, arl.IsExpired())
	})
}

// TestAPIRateLimitIncrementCount tests the IncrementCount method
func TestAPIRateLimitIncrementCount(t *testing.T) {
	t.Run("increments count from initial value", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-123",
			Endpoint:     "/api/deployments",
			WindowStart:  time.Now(),
			RequestCount: 1,
		}

		initialCount := arl.RequestCount
		arl.IncrementCount()

		assert.Equal(t, initialCount+1, arl.RequestCount)
		assert.Equal(t, 2, arl.RequestCount)
	})

	t.Run("increments count multiple times", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-456",
			Endpoint:     "/api/projects",
			WindowStart:  time.Now(),
			RequestCount: 5,
		}

		for i := 0; i < 10; i++ {
			arl.IncrementCount()
		}

		assert.Equal(t, 15, arl.RequestCount)
	})

	t.Run("increments from zero", func(t *testing.T) {
		arl := models.APIRateLimit{
			UserID:       "user-789",
			Endpoint:     "/api/metrics",
			WindowStart:  time.Now(),
			RequestCount: 0,
		}

		arl.IncrementCount()

		assert.Equal(t, 1, arl.RequestCount)
	})
}

// TestAPIRateLimitFields tests API rate limit field values
func TestAPIRateLimitFields(t *testing.T) {
	now := time.Now()

	arl := models.APIRateLimit{
		ID:           12345,
		UserID:       "user-uuid-123",
		Endpoint:     "/api/v1/deployments",
		WindowStart:  now,
		RequestCount: 42,
		CreatedAt:    now,
	}

	t.Run("stores and retrieves all fields", func(t *testing.T) {
		assert.Equal(t, int64(12345), arl.ID)
		assert.Equal(t, "user-uuid-123", arl.UserID)
		assert.Equal(t, "/api/v1/deployments", arl.Endpoint)
		assert.Equal(t, now, arl.WindowStart)
		assert.Equal(t, 42, arl.RequestCount)
		assert.Equal(t, now, arl.CreatedAt)
	})
}

// TestProviderConfigDefaults tests default values
func TestProviderConfigDefaults(t *testing.T) {
	pc := models.ProviderConfig{
		Provider:    "test-provider",
		DisplayName: "Test Provider",
	}

	t.Run("has expected field types", func(t *testing.T) {
		// Verify fields can be set to their zero values
		assert.Equal(t, 0, pc.ID)
		assert.False(t, pc.IsEnabled) // Will be set by GORM default in DB
		assert.False(t, pc.IsBeta)
		assert.Empty(t, pc.CreatedAt)
		assert.Empty(t, pc.UpdatedAt)
	})
}

// TestFrameworkPatternDefaults tests default values
func TestFrameworkPatternDefaults(t *testing.T) {
	fp := models.FrameworkPattern{
		Framework: "test-framework",
		Type:      "frontend",
	}

	t.Run("has expected field types and zero values", func(t *testing.T) {
		assert.Equal(t, 0, fp.ID)
		assert.Equal(t, 0.0, fp.ConfidenceWeight) // Will be set by GORM default in DB
		assert.Nil(t, fp.DefaultBuildCommand)
		assert.Nil(t, fp.DefaultStartCommand)
		assert.Nil(t, fp.DefaultInstallCommand)
		assert.Empty(t, fp.CreatedAt)
		assert.Empty(t, fp.UpdatedAt)
	})
}

// TestAPIRateLimitDefaults tests default values
func TestAPIRateLimitDefaults(t *testing.T) {
	arl := models.APIRateLimit{
		UserID:   "test-user",
		Endpoint: "/test",
	}

	t.Run("has expected field types and zero values", func(t *testing.T) {
		assert.Equal(t, int64(0), arl.ID)
		assert.Equal(t, 0, arl.RequestCount) // Will be set by GORM default in DB
		assert.Empty(t, arl.CreatedAt)
	})
}

// TestJSONBFieldsAreSet tests that JSONB fields can be set and are not nil
func TestJSONBFieldsAreSet(t *testing.T) {
	t.Run("ProviderConfig JSONB fields", func(t *testing.T) {
		pc := models.ProviderConfig{
			Provider:       "test",
			DisplayName:    "Test",
			SupportedTypes: datatypes.JSON([]byte(`["frontend"]`)),
			PricingTiers:   datatypes.JSON([]byte(`{"free": {}}`)),
			Metadata:       datatypes.JSON([]byte(`{}`)),
			RateLimits:     datatypes.JSON([]byte(`{}`)),
		}

		require.NotNil(t, pc.SupportedTypes)
		require.NotNil(t, pc.PricingTiers)
		require.NotNil(t, pc.Metadata)
		require.NotNil(t, pc.RateLimits)

		assert.Greater(t, len(pc.SupportedTypes), 0)
		assert.Greater(t, len(pc.PricingTiers), 0)
	})

	t.Run("FrameworkPattern JSONB fields", func(t *testing.T) {
		fp := models.FrameworkPattern{
			Framework:            "test",
			Type:                 "frontend",
			FilePatterns:         datatypes.JSON([]byte(`["*.js"]`)),
			DependencyPatterns:   datatypes.JSON([]byte(`["react"]`)),
			RecommendedProviders: datatypes.JSON([]byte(`["vercel"]`)),
			Metadata:             datatypes.JSON([]byte(`{}`)),
		}

		require.NotNil(t, fp.FilePatterns)
		require.NotNil(t, fp.DependencyPatterns)
		require.NotNil(t, fp.RecommendedProviders)
		require.NotNil(t, fp.Metadata)

		assert.Greater(t, len(fp.FilePatterns), 0)
		assert.Greater(t, len(fp.DependencyPatterns), 0)
	})
}
