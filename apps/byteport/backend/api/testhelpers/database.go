package testhelpers

import (
	"context"
	"database/sql"
	"fmt"
	"testing"
	"time"

	"github.com/testcontainers/testcontainers-go"
	postgrescontainer "github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
	postgresdriver "gorm.io/driver/postgres"
	sqlitedriver "gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// TestDB wraps a test database connection
type TestDB struct {
	DB        *gorm.DB
	Container *postgrescontainer.PostgresContainer
	ConnStr   string
}

// SetupTestDB creates a PostgreSQL container and returns a GORM DB connection
func SetupTestDB(t *testing.T) *TestDB {
	t.Helper()

	ctx := context.Background()
	
	// Create PostgreSQL container
	pgContainer, err := postgrescontainer.Run(ctx,
		"postgres:15-alpine",
		postgrescontainer.WithDatabase("testdb"),
		postgrescontainer.WithUsername("testuser"),
		postgrescontainer.WithPassword("testpass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(30*time.Second),
		),
	)
	if err != nil {
		t.Fatalf("Failed to start PostgreSQL container: %v", err)
	}

	// Get connection string
	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("Failed to get connection string: %v", err)
	}

	// Connect with GORM
	db, err := gorm.Open(postgresdriver.Open(connStr), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent), // Reduce test noise
	})
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}

	// Verify connection
	sqlDB, err := db.DB()
	if err != nil {
		t.Fatalf("Failed to get underlying sql.DB: %v", err)
	}

	if err := sqlDB.Ping(); err != nil {
		t.Fatalf("Failed to ping database: %v", err)
	}

	testDB := &TestDB{
		DB:        db,
		Container: pgContainer,
		ConnStr:   connStr,
	}

	// Register cleanup
	t.Cleanup(func() {
		testDB.Cleanup()
	})

	return testDB
}

// SetupSQLiteTestDB provides an in-memory SQLite database for fast unit tests.
func SetupSQLiteTestDB(t *testing.T) *TestDB {
	t.Helper()

	db, err := gorm.Open(sqlitedriver.Open("file::memory:?cache=shared"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		t.Fatalf("Failed to open in-memory sqlite database: %v", err)
	}

	testDB := &TestDB{
		DB: db,
	}

	t.Cleanup(func() {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	})

	return testDB
}

// Cleanup closes the database connection and terminates the container
func (tdb *TestDB) Cleanup() {
	if tdb.DB != nil {
		sqlDB, err := tdb.DB.DB()
		if err == nil {
			sqlDB.Close()
		}
	}
	
	if tdb.Container != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()
		tdb.Container.Terminate(ctx)
	}
}

// ResetTables truncates all tables (useful between tests)
func (tdb *TestDB) ResetTables(tableNames ...string) error {
	for _, table := range tableNames {
		if err := tdb.DB.Exec(fmt.Sprintf("TRUNCATE TABLE %s CASCADE", table)).Error; err != nil {
			return fmt.Errorf("failed to truncate table %s: %w", table, err)
		}
	}
	return nil
}

// RunInTransaction runs a function within a database transaction that gets rolled back
func (tdb *TestDB) RunInTransaction(fn func(*gorm.DB) error) error {
	return tdb.DB.Transaction(func(tx *gorm.DB) error {
		if err := fn(tx); err != nil {
			return err // This will cause rollback
		}
		// Force rollback even on success for testing
		return fmt.Errorf("test rollback")
	})
}

// GetRawDB returns the underlying *sql.DB for advanced operations
func (tdb *TestDB) GetRawDB() (*sql.DB, error) {
	return tdb.DB.DB()
}

// MigrateModels runs GORM AutoMigrate for the given models
func (tdb *TestDB) MigrateModels(models ...interface{}) error {
	return tdb.DB.AutoMigrate(models...)
}
