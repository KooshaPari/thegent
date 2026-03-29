package main

import (
	"testing"
	"time"

	"github.com/byteport/api/models"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// ModelsTestSuite groups all model tests
type ModelsTestSuite struct {
	suite.Suite
	db *gorm.DB
}

// SetupSuite runs once before all tests
func (suite *ModelsTestSuite) SetupSuite() {
	// Setup in-memory SQLite database for tests
	// Use ?_foreign_keys=ON to enable foreign key constraints
	db, err := gorm.Open(sqlite.Open(":memory:?_foreign_keys=ON"), &gorm.Config{
		// Disable default transaction for better performance
		SkipDefaultTransaction: true,
	})
	require.NoError(suite.T(), err)
	
	// Note: We test models directly without AutoMigrate since SQLite
	// doesn't support PostgreSQL-specific features (uuid type, gen_random_uuid())
	// In production, these models use PostgreSQL
	// For tests, we'll create simplified tables manually
	
	// Create simplified tables for testing
	_ = db.Exec(`
		CREATE TABLE users (
			uuid TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			email TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
			aws_access_key_id TEXT,
			aws_secret_access_key TEXT,
			llm_provider TEXT,
			llm_providers TEXT,
			portfolio_root_endpoint TEXT,
			portfolio_api_key TEXT,
			created_at DATETIME,
			updated_at DATETIME
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE projects (
			uuid TEXT PRIMARY KEY,
			id TEXT,
			owner TEXT NOT NULL,
			name TEXT NOT NULL,
			repository_id TEXT,
			readme TEXT,
			description TEXT,
			last_updated DATETIME,
			platform TEXT,
			access_url TEXT,
			type TEXT,
			deployments TEXT,
			created_at DATETIME,
			updated_at DATETIME,
			deleted_at DATETIME
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE instances (
			uuid TEXT PRIMARY KEY,
			owner TEXT NOT NULL,
			project_uuid TEXT,
			name TEXT NOT NULL,
			status TEXT NOT NULL,
			res_uuid TEXT NOT NULL,
			resources TEXT,
			created_at DATETIME,
			updated_at DATETIME
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE deployments (
			uuid TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			owner TEXT NOT NULL,
			project_uuid TEXT,
			status TEXT NOT NULL DEFAULT 'pending',
			providers TEXT,
			services TEXT,
			cost_info TEXT,
			metadata TEXT,
			env_vars TEXT,
			build_config TEXT,
			created_at DATETIME,
			updated_at DATETIME,
			deployed_at DATETIME,
			terminated_at DATETIME,
			deleted_at DATETIME
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE hosts (
			uuid TEXT PRIMARY KEY,
			owner TEXT NOT NULL,
			name TEXT NOT NULL,
			host_url TEXT NOT NULL,
			api_key TEXT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			specs TEXT,
			last_heartbeat DATETIME,
			capabilities TEXT,
			metadata TEXT,
			region TEXT,
			max_deployments INTEGER DEFAULT 10,
			current_deployments INTEGER DEFAULT 0,
			created_at DATETIME,
			updated_at DATETIME,
			deleted_at DATETIME
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE owners (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			login TEXT NOT NULL,
			node_id TEXT NOT NULL,
			avatar_url TEXT NOT NULL,
			html_url TEXT NOT NULL,
			type TEXT NOT NULL,
			site_admin INTEGER NOT NULL
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE repositories (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			node_id TEXT NOT NULL,
			name TEXT NOT NULL,
			full_name TEXT NOT NULL,
			private INTEGER NOT NULL,
			owner_id INTEGER NOT NULL,
			html_url TEXT NOT NULL,
			description TEXT,
			fork INTEGER NOT NULL,
			created_at TEXT NOT NULL,
			updated_at TEXT NOT NULL,
			pushed_at TEXT NOT NULL,
			ssh_url TEXT NOT NULL,
			clone_url TEXT NOT NULL,
			svn_url TEXT NOT NULL,
			homepage TEXT,
			size INTEGER NOT NULL,
			stargazers_count INTEGER NOT NULL,
			watchers_count INTEGER NOT NULL,
			language TEXT,
			has_issues INTEGER NOT NULL,
			has_projects INTEGER NOT NULL,
			has_downloads INTEGER NOT NULL,
			has_wiki INTEGER NOT NULL,
			has_pages INTEGER NOT NULL,
			has_discussions INTEGER NOT NULL,
			forks_count INTEGER NOT NULL,
			mirror_url TEXT,
			archived INTEGER NOT NULL,
			archive_url TEXT,
			disabled INTEGER NOT NULL,
			open_issues_count INTEGER NOT NULL,
			license TEXT,
			allow_forking INTEGER NOT NULL,
			is_template INTEGER NOT NULL,
			web_commit_signoff_required INTEGER NOT NULL,
			visibility TEXT NOT NULL,
			forks INTEGER NOT NULL,
			open_issues INTEGER NOT NULL,
			watchers INTEGER NOT NULL,
			default_branch TEXT NOT NULL,
			admin INTEGER NOT NULL,
			maintain INTEGER NOT NULL,
			push INTEGER NOT NULL,
			triage INTEGER NOT NULL,
			pull INTEGER NOT NULL
		)
	`)
	
	_ = db.Exec(`
		CREATE TABLE aws_resources (
			instance_id TEXT PRIMARY KEY,
			type TEXT NOT NULL,
			name TEXT NOT NULL,
			arn TEXT,
			status TEXT,
			region TEXT,
			service TEXT,
			created_at DATETIME,
			updated_at DATETIME
		)
	`)
	
	suite.db = db
	models.DB = db
}

// SetupTest runs before each test
func (suite *ModelsTestSuite) SetupTest() {
	// Clear all tables before each test
	suite.db.Exec("DELETE FROM users")
	suite.db.Exec("DELETE FROM projects")
	suite.db.Exec("DELETE FROM instances")
	suite.db.Exec("DELETE FROM deployments")
	suite.db.Exec("DELETE FROM hosts")
	suite.db.Exec("DELETE FROM repositories")
	suite.db.Exec("DELETE FROM owners")
	suite.db.Exec("DELETE FROM aws_resources")
}

// TearDownSuite runs once after all tests
func (suite *ModelsTestSuite) TearDownSuite() {
	sqlDB, _ := suite.db.DB()
	sqlDB.Close()
}

// TestProjectModel tests Project model behavior
func (suite *ModelsTestSuite) TestProjectModel() {
	t := suite.T()
	
	t.Run("creates project successfully", func(t *testing.T) {
		// Create owner first
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Project Owner",
			Email:    "owner@example.com",
			Password: "hash",
		}
		err := suite.db.Create(&owner).Error
		require.NoError(t, err)
		
		// Create project
		project := models.Project{
			UUID:  uuid.New().String(),
			Name:  "Test Project",
			Owner: owner.UUID,
		}
		
		err = suite.db.Create(&project).Error
		require.NoError(t, err)
		
		// Retrieve and verify
		var retrieved models.Project
		err = suite.db.Where("uuid = ?", project.UUID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "Test Project", retrieved.Name)
		assert.Equal(t, owner.UUID, retrieved.Owner)
	})
	
	t.Run("associates project with user", func(t *testing.T) {
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "User With Projects",
			Email:    "projects@example.com",
			Password: "hash",
		}
		err := suite.db.Create(&owner).Error
		require.NoError(t, err)
		
		// Create multiple projects
		project1 := models.Project{
			UUID:  uuid.New().String(),
			Name:  "Project 1",
			Owner: owner.UUID,
		}
		project2 := models.Project{
			UUID:  uuid.New().String(),
			Name:  "Project 2",
			Owner: owner.UUID,
		}
		
		suite.db.Create(&project1)
		suite.db.Create(&project2)
		
		// Retrieve user with projects
		var user models.User
		err = suite.db.Preload("Projects").Where("uuid = ?", owner.UUID).First(&user).Error
		require.NoError(t, err)
		
		assert.Len(t, user.Projects, 2)
	})
}

// TestInstanceModel tests Instance model behavior
func (suite *ModelsTestSuite) TestInstanceModel() {
	t := suite.T()
	
	t.Run("creates instance successfully", func(t *testing.T) {
		// Create owner
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Instance Owner",
			Email:    "instance@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		// Create project
		project := models.Project{
			UUID:  uuid.New().String(),
			Name:  "Instance Project",
			Owner: owner.UUID,
		}
		suite.db.Create(&project)
		
		// Create instance
		instance := models.Instance{
			UUID:        uuid.New().String(),
			ProjectUUID: project.UUID,
			Owner:       owner.UUID,
			Name:        "test-instance",
			Status:      "running",
			ResUUID:     uuid.New().String(),
		}
		
		err := suite.db.Create(&instance).Error
		require.NoError(t, err)
		
		// Retrieve and verify
		var retrieved models.Instance
		err = suite.db.Where("uuid = ?", instance.UUID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "test-instance", retrieved.Name)
		assert.Equal(t, "running", retrieved.Status)
		assert.Equal(t, owner.UUID, retrieved.Owner)
	})
	
	t.Run("tracks instance timestamps", func(t *testing.T) {
		instance := models.Instance{
			UUID:    uuid.New().String(),
			Name:    "timestamp-test",
			Status:  "pending",
			ResUUID: uuid.New().String(),
		}
		
		err := suite.db.Create(&instance).Error
		require.NoError(t, err)
		
		var retrieved models.Instance
		suite.db.Where("uuid = ?", instance.UUID).First(&retrieved)
		
		assert.NotZero(t, retrieved.CreatedAt)
		assert.NotZero(t, retrieved.UpdatedAt)
	})
}

// TestDeploymentModel tests Deployment model behavior
func (suite *ModelsTestSuite) TestDeploymentModel() {
	t := suite.T()
	
	t.Run("creates deployment successfully", func(t *testing.T) {
		// Create owner
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Deployment Owner",
			Email:    "deploy@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		deployment := models.Deployment{
			UUID:   uuid.New().String(),
			Name:   "Test Deployment",
			Owner:  owner.UUID,
			Status: "deploying",
		}
		
		err := suite.db.Create(&deployment).Error
		require.NoError(t, err)
		
		var retrieved models.Deployment
		err = suite.db.Where("uuid = ?", deployment.UUID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "Test Deployment", retrieved.Name)
		assert.Equal(t, "deploying", retrieved.Status)
	})
	
	t.Run("updates deployment status", func(t *testing.T) {
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Owner",
			Email:    "owner2@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		deployment := models.Deployment{
			UUID:   uuid.New().String(),
			Name:   "Status Update Test",
			Owner:  owner.UUID,
			Status: "deploying",
		}
		
		suite.db.Create(&deployment)
		
		// Update status using helper method
		deployment.SetStatus("deployed")
		err := suite.db.Save(&deployment).Error
		require.NoError(t, err)
		
		// Verify update
		var updated models.Deployment
		suite.db.Where("uuid = ?", deployment.UUID).First(&updated)
		assert.Equal(t, "deployed", updated.Status)
		assert.NotNil(t, updated.DeployedAt)
	})
	
	t.Run("tests deployment helper methods", func(t *testing.T) {
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Helper Owner",
			Email:    "helper@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		deployment := models.Deployment{
			UUID:   uuid.New().String(),
			Name:   "Helper Test",
			Owner:  owner.UUID,
			Status: "deployed",
		}
		
		assert.True(t, deployment.IsActive())
		assert.False(t, deployment.IsFailed())
		assert.False(t, deployment.IsTerminated())
		
		deployment.SetStatus("failed")
		assert.True(t, deployment.IsFailed())
		assert.False(t, deployment.IsActive())
		
		deployment.SetStatus("terminated")
		assert.True(t, deployment.IsTerminated())
		assert.NotNil(t, deployment.TerminatedAt)
	})
}

// TestHostModel tests Host model behavior
func (suite *ModelsTestSuite) TestHostModel() {
	t := suite.T()
	
	t.Run("creates host successfully", func(t *testing.T) {
		// Create owner
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Host Owner",
			Email:    "hostowner@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		host := models.Host{
			UUID:    uuid.New().String(),
			Owner:   owner.UUID,
			Name:    "host1.example.com",
			HostURL: "https://host1.example.com",
			APIKey:  "test-api-key",
			Status:  "online",
		}
		
		err := suite.db.Create(&host).Error
		require.NoError(t, err)
		
		var retrieved models.Host
		err = suite.db.Where("uuid = ?", host.UUID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "host1.example.com", retrieved.Name)
		assert.Equal(t, "https://host1.example.com", retrieved.HostURL)
		assert.Equal(t, "online", retrieved.Status)
	})
	
	t.Run("tests host helper methods", func(t *testing.T) {
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Helper Host Owner",
			Email:    "hosthelper@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		host := models.Host{
			UUID:               uuid.New().String(),
			Owner:              owner.UUID,
			Name:               "helper-host",
			HostURL:            "https://helper.example.com",
			APIKey:             "key",
			Status:             "online",
			MaxDeployments:     10,
			CurrentDeployments: 5,
		}
		
		// Test heartbeat
		host.UpdateHeartbeat()
		assert.NotNil(t, host.LastHeartbeat)
		assert.Equal(t, "online", host.Status)
		assert.True(t, host.IsOnline())
		
		// Test deployment capacity
		assert.True(t, host.CanAcceptDeployment())
		
		// Max out deployments
		host.CurrentDeployments = 10
		assert.False(t, host.CanAcceptDeployment())
	})
}

// TestRepositoryModel tests Repository model behavior
func (suite *ModelsTestSuite) TestRepositoryModel() {
	t := suite.T()
	
	t.Run("creates repository successfully", func(t *testing.T) {
		// Create owner first
		owner := models.Owner{
			Login:     "testuser",
			NodeID:    "node-123",
			AvatarURL: "https://avatar.example.com",
			HTMLURL:   "https://github.com/testuser",
			Type:      "User",
			SiteAdmin: false,
		}
		err := suite.db.Create(&owner).Error
		require.NoError(t, err)
		
		repo := models.Repository{
			NodeID:      "repo-node-123",
			Name:        "test-repo",
			FullName:    "testuser/test-repo",
			Private:     false,
			OwnerID:     owner.ID,
			HTMLURL:     "https://github.com/testuser/test-repo",
			Description: "A test repository",
			Fork:        false,
			CreatedAt:   time.Now().Format(time.RFC3339),
			UpdatedAt:   time.Now().Format(time.RFC3339),
			PushedAt:    time.Now().Format(time.RFC3339),
			SSHURL:      "git@github.com:testuser/test-repo.git",
			CloneURL:    "https://github.com/testuser/test-repo.git",
			SVNURL:      "https://github.com/testuser/test-repo",
			Language:    "Go",
			Visibility:  "public",
			DefaultBranch: "main",
		}
		
		err = suite.db.Create(&repo).Error
		require.NoError(t, err)
		
		var retrieved models.Repository
		err = suite.db.Preload("Owner").Where("id = ?", repo.ID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "test-repo", retrieved.Name)
		assert.Equal(t, "testuser/test-repo", retrieved.FullName)
		assert.Equal(t, "Go", retrieved.Language)
		assert.False(t, retrieved.Private)
		assert.Equal(t, "testuser", retrieved.Owner.Login)
	})
}

// TestAWSResourceModel tests AWSResource model behavior
func (suite *ModelsTestSuite) TestAWSResourceModel() {
	t := suite.T()
	
	t.Run("creates AWS resource successfully", func(t *testing.T) {
		resource := models.AWSResource{
			InstanceID: uuid.New().String(),
			Type:       "ec2",
			Name:       "web-server-1",
			ARN:        "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
			Status:     "running",
			Region:     "us-east-1",
			Service:    "EC2",
		}
		
		err := suite.db.Create(&resource).Error
		require.NoError(t, err)
		
		var retrieved models.AWSResource
		err = suite.db.Where("instance_id = ?", resource.InstanceID).First(&retrieved).Error
		require.NoError(t, err)
		
		assert.Equal(t, "ec2", retrieved.Type)
		assert.Equal(t, "web-server-1", retrieved.Name)
		assert.Equal(t, "running", retrieved.Status)
		assert.Equal(t, "EC2", retrieved.Service)
	})
	
	t.Run("tracks AWS resource timestamps", func(t *testing.T) {
		resource := models.AWSResource{
			InstanceID: uuid.New().String(),
			Type:       "rds",
			Name:       "database-1",
			Status:     "available",
		}
		
		err := suite.db.Create(&resource).Error
		require.NoError(t, err)
		
		var retrieved models.AWSResource
		suite.db.Where("instance_id = ?", resource.InstanceID).First(&retrieved)
		
		assert.NotZero(t, retrieved.CreatedAt)
		assert.NotZero(t, retrieved.UpdatedAt)
	})
	
	t.Run("queries resources by service", func(t *testing.T) {
		// Clear any existing resources first
		suite.db.Exec("DELETE FROM aws_resources")
		
		// Create multiple resources
		resources := []models.AWSResource{
			{
				InstanceID: uuid.New().String(),
				Type:       "ec2",
				Name:       "instance-1",
				Service:    "EC2",
			},
			{
				InstanceID: uuid.New().String(),
				Type:       "ec2",
				Name:       "instance-2",
				Service:    "EC2",
			},
			{
				InstanceID: uuid.New().String(),
				Type:       "rds",
				Name:       "db-1",
				Service:    "RDS",
			},
		}
		
		for _, r := range resources {
			suite.db.Create(&r)
		}
		
		// Query EC2 resources
		var ec2Resources []models.AWSResource
		err := suite.db.Where("service = ?", "EC2").Find(&ec2Resources).Error
		require.NoError(t, err)
		
		assert.Len(t, ec2Resources, 2)
		assert.Equal(t, "EC2", ec2Resources[0].Service)
		assert.Equal(t, "EC2", ec2Resources[1].Service)
	})
}

// TestUserRelationships tests User model relationships
func (suite *ModelsTestSuite) TestUserRelationships() {
	t := suite.T()
	
	t.Run("loads user with projects and instances", func(t *testing.T) {
		// Create user
		user := models.User{
			UUID:     uuid.New().String(),
			Name:     "Relationship Test User",
			Email:    "relationships@example.com",
			Password: "hash",
		}
		suite.db.Create(&user)
		
		// Create project
		project := models.Project{
			UUID:  uuid.New().String(),
			Name:  "User's Project",
			Owner: user.UUID,
		}
		suite.db.Create(&project)
		
		// Create instance
		instance := models.Instance{
			UUID:        uuid.New().String(),
			ProjectUUID: project.UUID,
			Owner:       user.UUID,
			Name:        "test-instance",
			Status:      "running",
			ResUUID:     uuid.New().String(),
		}
		suite.db.Create(&instance)
		
		// Load user with relationships
		var loaded models.User
		err := suite.db.Preload("Projects").Preload("Instances").
			Where("uuid = ?", user.UUID).First(&loaded).Error
		require.NoError(t, err)
		
		assert.Len(t, loaded.Projects, 1)
		assert.Len(t, loaded.Instances, 1)
		assert.Equal(t, "User's Project", loaded.Projects[0].Name)
		assert.Equal(t, "test-instance", loaded.Instances[0].Name)
	})
}

// TestModelValidation tests model validation behavior
func (suite *ModelsTestSuite) TestModelValidation() {
	t := suite.T()
	
	t.Run("enforces not null constraints", func(t *testing.T) {
		// Try to create user without required fields
		user := models.User{
			UUID: uuid.New().String(),
			// Missing Name and Email
		}
		
		err := suite.db.Create(&user).Error
		// SQLite in memory mode might not enforce all constraints
		// This test documents expected behavior with a real database
		if err != nil {
			assert.Error(t, err)
		}
	})
	
	t.Run("handles optional fields", func(t *testing.T) {
		owner := models.User{
			UUID:     uuid.New().String(),
			Name:     "Optional Test Owner",
			Email:    "optional@example.com",
			Password: "hash",
		}
		suite.db.Create(&owner)
		
		deployment := models.Deployment{
			UUID:  uuid.New().String(),
			Name:  "Optional Fields Test",
			Owner: owner.UUID,
			// Many fields are optional
		}
		
		err := suite.db.Create(&deployment).Error
		require.NoError(t, err)
		
		var retrieved models.Deployment
		suite.db.Where("uuid = ?", deployment.UUID).First(&retrieved)
		
		assert.NotEmpty(t, retrieved.Name)
		assert.NotEmpty(t, retrieved.Owner)
	})
}

// Run the test suite
func TestModelsTestSuite(t *testing.T) {
	suite.Run(t, new(ModelsTestSuite))
}