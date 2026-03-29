package testhelpers

import (
	"time"

	"github.com/google/uuid"
)

// TestUser represents a test user fixture
type TestUser struct {
	ID       string `json:"id" gorm:"type:uuid;primary_key"`
	Email    string `json:"email" gorm:"uniqueIndex"`
	Name     string `json:"name"`
	WorkOSID string `json:"workos_id" gorm:"uniqueIndex"`
	IsActive bool   `json:"is_active"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// TestProject represents a test project fixture
type TestProject struct {
	ID          string    `json:"id" gorm:"type:uuid;primary_key"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	UserID      string    `json:"user_id" gorm:"type:uuid;index"`
	GitURL      string    `json:"git_url"`
	Framework   string    `json:"framework"`
	Status      string    `json:"status"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// TestDeployment represents a test deployment fixture
type TestDeployment struct {
	ID        string    `json:"id" gorm:"type:uuid;primary_key"`
	ProjectID string    `json:"project_id" gorm:"type:uuid;index"`
	Version   string    `json:"version"`
	Status    string    `json:"status"`
	Provider  string    `json:"provider"`
	URL       string    `json:"url"`
	BuildLog  string    `json:"build_log"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// UserFixtures provides common user test data
var UserFixtures = struct {
	Alice   TestUser
	Bob     TestUser
	Charlie TestUser
}{
	Alice: TestUser{
		ID:       "550e8400-e29b-41d4-a716-446655440001",
		Email:    "alice@example.com",
		Name:     "Alice Smith",
		WorkOSID: "user_01H5JQDQR7GFKDM2NV7JVXPG4K",
		IsActive: true,
		CreatedAt: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
	},
	Bob: TestUser{
		ID:       "550e8400-e29b-41d4-a716-446655440002",
		Email:    "bob@example.com",
		Name:     "Bob Johnson",
		WorkOSID: "user_01H5JQDQR7GFKDM2NV7JVXPG4L",
		IsActive: true,
		CreatedAt: time.Date(2024, 1, 2, 0, 0, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 2, 0, 0, 0, 0, time.UTC),
	},
	Charlie: TestUser{
		ID:       "550e8400-e29b-41d4-a716-446655440003",
		Email:    "charlie@example.com",
		Name:     "Charlie Brown",
		WorkOSID: "user_01H5JQDQR7GFKDM2NV7JVXPG4M",
		IsActive: false,
		CreatedAt: time.Date(2024, 1, 3, 0, 0, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 3, 0, 0, 0, 0, time.UTC),
	},
}

// ProjectFixtures provides common project test data
var ProjectFixtures = struct {
	NextJSApp TestProject
	GoAPI     TestProject
	ReactSPA  TestProject
}{
	NextJSApp: TestProject{
		ID:          "660e8400-e29b-41d4-a716-446655440001",
		Name:        "My Next.js App",
		Description: "A modern Next.js application",
		UserID:      UserFixtures.Alice.ID,
		GitURL:      "https://github.com/alice/nextjs-app.git",
		Framework:   "nextjs",
		Status:      "active",
		CreatedAt:   time.Date(2024, 1, 10, 0, 0, 0, 0, time.UTC),
		UpdatedAt:   time.Date(2024, 1, 10, 0, 0, 0, 0, time.UTC),
	},
	GoAPI: TestProject{
		ID:          "660e8400-e29b-41d4-a716-446655440002",
		Name:        "REST API",
		Description: "Go-based REST API",
		UserID:      UserFixtures.Bob.ID,
		GitURL:      "https://github.com/bob/go-api.git",
		Framework:   "go",
		Status:      "active",
		CreatedAt:   time.Date(2024, 1, 11, 0, 0, 0, 0, time.UTC),
		UpdatedAt:   time.Date(2024, 1, 11, 0, 0, 0, 0, time.UTC),
	},
	ReactSPA: TestProject{
		ID:          "660e8400-e29b-41d4-a716-446655440003",
		Name:        "React Dashboard",
		Description: "React single page application",
		UserID:      UserFixtures.Alice.ID,
		GitURL:      "https://github.com/alice/react-dashboard.git",
		Framework:   "react",
		Status:      "archived",
		CreatedAt:   time.Date(2024, 1, 12, 0, 0, 0, 0, time.UTC),
		UpdatedAt:   time.Date(2024, 1, 15, 0, 0, 0, 0, time.UTC),
	},
}

// DeploymentFixtures provides common deployment test data
var DeploymentFixtures = struct {
	Successful TestDeployment
	Failed     TestDeployment
	InProgress TestDeployment
}{
	Successful: TestDeployment{
		ID:        "770e8400-e29b-41d4-a716-446655440001",
		ProjectID: ProjectFixtures.NextJSApp.ID,
		Version:   "v1.0.0",
		Status:    "deployed",
		Provider:  "vercel",
		URL:       "https://my-nextjs-app-abc123.vercel.app",
		BuildLog:  "Build completed successfully\nDeployment ready",
		CreatedAt: time.Date(2024, 1, 20, 10, 0, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 20, 10, 5, 0, 0, time.UTC),
	},
	Failed: TestDeployment{
		ID:        "770e8400-e29b-41d4-a716-446655440002",
		ProjectID: ProjectFixtures.GoAPI.ID,
		Version:   "v0.1.0",
		Status:    "failed",
		Provider:  "render",
		URL:       "",
		BuildLog:  "Build failed: missing environment variable DATABASE_URL",
		CreatedAt: time.Date(2024, 1, 21, 14, 30, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 21, 14, 32, 0, 0, time.UTC),
	},
	InProgress: TestDeployment{
		ID:        "770e8400-e29b-41d4-a716-446655440003",
		ProjectID: ProjectFixtures.ReactSPA.ID,
		Version:   "v2.1.0",
		Status:    "building",
		Provider:  "netlify",
		URL:       "",
		BuildLog:  "Starting build...\nInstalling dependencies...",
		CreatedAt: time.Date(2024, 1, 22, 9, 15, 0, 0, time.UTC),
		UpdatedAt: time.Date(2024, 1, 22, 9, 17, 0, 0, time.UTC),
	},
}

// CreateTestUser creates a new test user with random ID if not provided
func CreateTestUser(overrides ...func(*TestUser)) TestUser {
	user := TestUser{
		ID:       uuid.New().String(),
		Email:    "test@example.com",
		Name:     "Test User",
		WorkOSID: "user_" + uuid.New().String()[:10],
		IsActive: true,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	
	for _, override := range overrides {
		override(&user)
	}
	
	return user
}

// CreateTestProject creates a new test project with random ID if not provided
func CreateTestProject(userID string, overrides ...func(*TestProject)) TestProject {
	project := TestProject{
		ID:          uuid.New().String(),
		Name:        "Test Project",
		Description: "A test project",
		UserID:      userID,
		GitURL:      "https://github.com/test/repo.git",
		Framework:   "nextjs",
		Status:      "active",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	
	for _, override := range overrides {
		override(&project)
	}
	
	return project
}

// CreateTestDeployment creates a new test deployment with random ID if not provided
func CreateTestDeployment(projectID string, overrides ...func(*TestDeployment)) TestDeployment {
	deployment := TestDeployment{
		ID:        uuid.New().String(),
		ProjectID: projectID,
		Version:   "v1.0.0",
		Status:    "deployed",
		Provider:  "vercel",
		URL:       "https://test-app.vercel.app",
		BuildLog:  "Build completed successfully",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	
	for _, override := range overrides {
		override(&deployment)
	}
	
	return deployment
}