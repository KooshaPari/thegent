package repositories

import (
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"github.com/google/uuid"
	"github.com/matryer/is"
)

func TestDeploymentRepository_InMemory(t *testing.T) {
	repo := NewInMemoryDeploymentRepository()
	testDeploymentRepository(t, repo)
}

func TestDeploymentRepository_GORM(t *testing.T) {
	testDB := setupTestDB(t)

	// Run migrations
	err := testDB.MigrateModels(&Deployment{})
	if err != nil {
		t.Fatalf("Failed to migrate models: %v", err)
	}

	repo := NewGormDeploymentRepository(testDB.DB)
	testDeploymentRepository(t, repo)
}

// testDeploymentRepository runs common tests against any DeploymentRepository implementation
func testDeploymentRepository(t *testing.T, repo DeploymentRepository) {
	t.Helper()

	testCases := []struct {
		name string
		test func(t *testing.T, repo DeploymentRepository)
	}{
		{"Create", testCreate},
		{"GetByID", testGetByID},
		{"GetByUserID", testGetByUserID},
		{"Update", testUpdate},
		{"Delete", testDelete},
		{"List", testList},
		{"GetByStatus", testGetByStatus},
		{"GetByProvider", testGetByProvider},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			tc.test(t, repo)
		})
	}
}

func testCreate(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	deployment := &Deployment{
		Name:     "Test App",
		Type:     "frontend",
		Provider: "vercel",
		Status:   "deploying",
		UserID:   uuid.New().String(),
		GitURL:   "https://github.com/test/app.git",
		Branch:   "main",
		EnvVars: EnvVarMap{
			"NODE_ENV": "production",
		},
	}

	// Test create
	err := repo.Create(deployment)
	is.NoErr(err)                           // Create should succeed
	is.True(deployment.ID != "")            // ID should be generated
	is.True(!deployment.CreatedAt.IsZero()) // CreatedAt should be set
	is.True(!deployment.UpdatedAt.IsZero()) // UpdatedAt should be set

	// Test retrieve
	retrieved, err := repo.GetByID(deployment.ID)
	is.NoErr(err)             // GetByID should succeed
	is.True(retrieved != nil) // Retrieved deployment should not be nil

	// Compare the essential fields
	is.Equal(retrieved.Name, deployment.Name)
	is.Equal(retrieved.Type, deployment.Type)
	is.Equal(retrieved.Provider, deployment.Provider)
	is.Equal(retrieved.Status, deployment.Status)
	is.Equal(retrieved.UserID, deployment.UserID)
}

func testGetByID(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	// Test non-existent ID
	deployment, err := repo.GetByID(uuid.New().String())
	is.NoErr(err)              // GetByID should not error for non-existent ID
	is.True(deployment == nil) // Should return nil for non-existent deployment

	// Create test deployment
	testDeployment := &Deployment{
		Name:     "Test Deployment",
		Type:     "backend",
		Provider: "render",
		Status:   "deployed",
		UserID:   uuid.New().String(),
	}

	err = repo.Create(testDeployment)
	is.NoErr(err) // Create should succeed

	// Test existing ID
	retrieved, err := repo.GetByID(testDeployment.ID)
	is.NoErr(err)                             // GetByID should succeed
	is.True(retrieved != nil)                 // Retrieved deployment should not be nil
	is.Equal(retrieved.ID, testDeployment.ID) // IDs should match
}

func testGetByUserID(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	userID := uuid.New().String()

	// Test empty result
	deployments, err := repo.GetByUserID(userID)
	is.NoErr(err)                 // GetByUserID should succeed
	is.Equal(len(deployments), 0) // Should return empty slice for new user

	// Create test deployments
	deployment1 := &Deployment{
		Name:     "App 1",
		Type:     "frontend",
		Provider: "vercel",
		Status:   "deployed",
		UserID:   userID,
	}

	deployment2 := &Deployment{
		Name:     "App 2",
		Type:     "backend",
		Provider: "render",
		Status:   "failed",
		UserID:   userID,
	}

	deployment3 := &Deployment{
		Name:     "Other User App",
		Type:     "frontend",
		Provider: "netlify",
		Status:   "deployed",
		UserID:   uuid.New().String(),
	}

	err = repo.Create(deployment1)
	is.NoErr(err) // Create deployment1 should succeed

	err = repo.Create(deployment2)
	is.NoErr(err) // Create deployment2 should succeed

	err = repo.Create(deployment3)
	is.NoErr(err) // Create deployment3 should succeed

	// Test retrieval
	userDeployments, err := repo.GetByUserID(userID)
	is.NoErr(err)                     // GetByUserID should succeed
	is.Equal(len(userDeployments), 2) // Should return 2 deployments for the user

	// Verify deployments belong to correct user
	for _, dep := range userDeployments {
		is.Equal(dep.UserID, userID) // All deployments should belong to the user
	}
}

func testUpdate(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	// Create test deployment
	deployment := &Deployment{
		Name:     "Original Name",
		Type:     "frontend",
		Provider: "vercel",
		Status:   "deploying",
		UserID:   uuid.New().String(),
	}

	err := repo.Create(deployment)
	is.NoErr(err) // Create should succeed

	originalUpdatedAt := deployment.UpdatedAt
	time.Sleep(1 * time.Millisecond) // Ensure time difference

	// Update deployment
	deployment.Name = "Updated Name"
	deployment.Status = "deployed"
	deployment.URL = "https://updated-app.vercel.app"

	err = repo.Update(deployment)
	is.NoErr(err)                                          // Update should succeed
	is.True(deployment.UpdatedAt.After(originalUpdatedAt)) // UpdatedAt should be updated

	// Verify update
	updated, err := repo.GetByID(deployment.ID)
	is.NoErr(err)                                           // GetByID should succeed
	is.Equal(updated.Name, "Updated Name")                  // Name should be updated
	is.Equal(updated.Status, "deployed")                    // Status should be updated
	is.Equal(updated.URL, "https://updated-app.vercel.app") // URL should be updated
}

func testDelete(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	// Create test deployment
	deployment := &Deployment{
		Name:     "To Delete",
		Type:     "frontend",
		Provider: "netlify",
		Status:   "deployed",
		UserID:   uuid.New().String(),
	}

	err := repo.Create(deployment)
	is.NoErr(err) // Create should succeed

	// Verify it exists
	retrieved, err := repo.GetByID(deployment.ID)
	is.NoErr(err)             // GetByID should succeed
	is.True(retrieved != nil) // Deployment should exist

	// Delete it
	err = repo.Delete(deployment.ID)
	is.NoErr(err) // Delete should succeed

	// Verify it's gone
	deleted, err := repo.GetByID(deployment.ID)
	is.NoErr(err)           // GetByID should not error
	is.True(deleted == nil) // Deployment should no longer exist
}

func testList(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	// Test empty list
	deployments, err := repo.List()
	is.NoErr(err)                    // List should succeed
	initialCount := len(deployments) // Store initial count for comparison

	// Create test deployments
	deployments1 := []*Deployment{
		{
			Name:     "App A",
			Type:     "frontend",
			Provider: "vercel",
			Status:   "deployed",
			UserID:   uuid.New().String(),
		},
		{
			Name:     "App B",
			Type:     "backend",
			Provider: "render",
			Status:   "failed",
			UserID:   uuid.New().String(),
		},
	}

	for _, deployment := range deployments1 {
		err := repo.Create(deployment)
		is.NoErr(err) // Create should succeed
	}

	// Test list
	allDeployments, err := repo.List()
	is.NoErr(err)                                 // List should succeed
	is.Equal(len(allDeployments), initialCount+2) // Should have 2 more deployments
}

func testGetByStatus(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	status := "testing-status"

	// Test empty result
	deployments, err := repo.GetByStatus(status)
	is.NoErr(err)                    // GetByStatus should succeed
	initialCount := len(deployments) // Store initial count

	// Create deployments with different statuses
	deployments1 := []*Deployment{
		{
			Name:     "App 1",
			Type:     "frontend",
			Provider: "vercel",
			Status:   status,
			UserID:   uuid.New().String(),
		},
		{
			Name:     "App 2",
			Type:     "backend",
			Provider: "render",
			Status:   status,
			UserID:   uuid.New().String(),
		},
		{
			Name:     "App 3",
			Type:     "frontend",
			Provider: "netlify",
			Status:   "different-status",
			UserID:   uuid.New().String(),
		},
	}

	for _, deployment := range deployments1 {
		err := repo.Create(deployment)
		is.NoErr(err) // Create should succeed
	}

	// Test retrieval by status
	statusDeployments, err := repo.GetByStatus(status)
	is.NoErr(err)                                    // GetByStatus should succeed
	is.Equal(len(statusDeployments), initialCount+2) // Should have 2 deployments with the status

	// Verify all returned deployments have correct status
	for _, dep := range statusDeployments {
		is.Equal(dep.Status, status) // All deployments should have the correct status
	}
}

func testGetByProvider(t *testing.T, repo DeploymentRepository) {
	is := is.New(t)

	provider := "testing-provider"

	// Test empty result
	deployments, err := repo.GetByProvider(provider)
	is.NoErr(err)                    // GetByProvider should succeed
	initialCount := len(deployments) // Store initial count

	// Create deployments with different providers
	deployments1 := []*Deployment{
		{
			Name:     "App 1",
			Type:     "frontend",
			Provider: provider,
			Status:   "deployed",
			UserID:   uuid.New().String(),
		},
		{
			Name:     "App 2",
			Type:     "backend",
			Provider: provider,
			Status:   "failed",
			UserID:   uuid.New().String(),
		},
		{
			Name:     "App 3",
			Type:     "frontend",
			Provider: "different-provider",
			Status:   "deployed",
			UserID:   uuid.New().String(),
		},
	}

	for _, deployment := range deployments1 {
		err := repo.Create(deployment)
		is.NoErr(err) // Create should succeed
	}

	// Test retrieval by provider
	providerDeployments, err := repo.GetByProvider(provider)
	is.NoErr(err)                                      // GetByProvider should succeed
	is.Equal(len(providerDeployments), initialCount+2) // Should have 2 deployments with the provider

	// Verify all returned deployments have correct provider
	for _, dep := range providerDeployments {
		is.Equal(dep.Provider, provider) // All deployments should have the correct provider
	}
}

// Test fixtures using testhelpers
func TestDeploymentRepository_WithFixtures(t *testing.T) {
	is := is.New(t)
	repo := NewInMemoryDeploymentRepository()

	testUserID := uuid.New().String()

	// Create deployment using fixture-style approach
	deployment := &Deployment{
		Name:     "Fixture Test App",
		Type:     "frontend",
		Provider: "vercel",
		Status:   "deployed",
		UserID:   testUserID,
		URL:      "https://fixture-app.vercel.app",
		GitURL:   "https://github.com/test/fixture-app.git",
		Branch:   "main",
		EnvVars: EnvVarMap{
			"NODE_ENV": "production",
			"API_URL":  "https://api.fixture-app.com",
		},
	}

	err := repo.Create(deployment)
	is.NoErr(err) // Create should succeed

	retrieved, err := repo.GetByID(deployment.ID)
	is.NoErr(err)             // GetByID should succeed
	is.True(retrieved != nil) // Deployment should exist

	// Test complex field (environment variables)
	if diff := cmp.Diff(deployment.EnvVars, retrieved.EnvVars); diff != "" {
		t.Errorf("EnvVars mismatch (-want +got):\n%s", diff)
	}
}
