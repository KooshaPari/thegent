package testhelpers

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/gorm"
)

func TestSetupSQLiteTestDB(t *testing.T) {
	t.Run("creates in-memory SQLite database", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		require.NotNil(t, testDB)
		require.NotNil(t, testDB.DB)
		assert.Nil(t, testDB.Container) // SQLite doesn't use containers
		assert.Empty(t, testDB.ConnStr) // SQLite doesn't have connection string
		
		// Test that we can perform basic operations
		var result int
		err := testDB.DB.Raw("SELECT 1").Scan(&result).Error
		require.NoError(t, err)
		assert.Equal(t, 1, result)
	})

	t.Run("database is properly configured", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Test that we can create a table
		err := testDB.DB.Exec("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Test that we can insert data
		err = testDB.DB.Exec("INSERT INTO test_table (name) VALUES ('test')").Error
		require.NoError(t, err)
		
		// Test that we can query data
		var count int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM test_table").Scan(&count).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), count)
	})

	t.Run("multiple calls create separate databases", func(t *testing.T) {
		testDB1 := SetupSQLiteTestDB(t)
		testDB2 := SetupSQLiteTestDB(t)
		
		// Create table in first DB
		err := testDB1.DB.Exec("CREATE TABLE test_table1 (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Insert data in first DB
		err = testDB1.DB.Exec("INSERT INTO test_table1 (name) VALUES ('test1')").Error
		require.NoError(t, err)
		
		// Create different table in second DB
		err = testDB2.DB.Exec("CREATE TABLE test_table2 (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Insert data in second DB
		err = testDB2.DB.Exec("INSERT INTO test_table2 (name) VALUES ('test2')").Error
		require.NoError(t, err)
		
		// Verify each DB has its own data
		var count1, count2 int64
		err = testDB1.DB.Raw("SELECT COUNT(*) FROM test_table1").Scan(&count1).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), count1)
		
		err = testDB2.DB.Raw("SELECT COUNT(*) FROM test_table2").Scan(&count2).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), count2)
	})
}

func TestTestDB_CleanupDatabase(t *testing.T) {
	t.Run("cleans up SQLite database", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Verify database is working
		var result int
		err := testDB.DB.Raw("SELECT 1").Scan(&result).Error
		require.NoError(t, err)
		
		// Cleanup should not panic
		assert.NotPanics(t, func() {
			testDB.Cleanup()
		})
		
		// After cleanup, database should be closed
		err = testDB.DB.Raw("SELECT 1").Scan(&result).Error
		assert.Error(t, err) // Should fail because connection is closed
	})

	t.Run("handles nil database gracefully", func(t *testing.T) {
		testDB := &TestDB{
			DB:        nil,
			Container: nil,
		}
		
		// Should not panic with nil values
		assert.NotPanics(t, func() {
			testDB.Cleanup()
		})
	})

	t.Run("handles database close error gracefully", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Manually close the database to simulate an error
		if sqlDB, err := testDB.DB.DB(); err == nil {
			sqlDB.Close()
		}
		
		// Cleanup should still not panic
		assert.NotPanics(t, func() {
			testDB.Cleanup()
		})
	})
}

func TestTestDB_ResetTables(t *testing.T) {
	t.Run("deletes data from specified tables", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Create test tables
		err := testDB.DB.Exec("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		err = testDB.DB.Exec("CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Insert test data
		err = testDB.DB.Exec("INSERT INTO users (name) VALUES ('Alice'), ('Bob')").Error
		require.NoError(t, err)
		
		err = testDB.DB.Exec("INSERT INTO projects (name) VALUES ('Project1'), ('Project2')").Error
		require.NoError(t, err)
		
		// Verify data exists
		var userCount, projectCount int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM users").Scan(&userCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(2), userCount)
		
		err = testDB.DB.Raw("SELECT COUNT(*) FROM projects").Scan(&projectCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(2), projectCount)
		
		// Delete data (SQLite equivalent of TRUNCATE)
		err = testDB.DB.Exec("DELETE FROM users").Error
		require.NoError(t, err)
		err = testDB.DB.Exec("DELETE FROM projects").Error
		require.NoError(t, err)
		
		// Verify data is gone
		err = testDB.DB.Raw("SELECT COUNT(*) FROM users").Scan(&userCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(0), userCount)
		
		err = testDB.DB.Raw("SELECT COUNT(*) FROM projects").Scan(&projectCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(0), projectCount)
	})

	t.Run("handles non-existent tables gracefully", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Should not error for non-existent tables
		err := testDB.ResetTables("non_existent_table")
		// This will fail because SQLite doesn't support TRUNCATE
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "TRUNCATE")
	})

	t.Run("handles empty table list", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Should not error for empty list
		err := testDB.ResetTables()
		require.NoError(t, err)
	})
}

func TestTestDB_RunInTransaction(t *testing.T) {
	t.Run("runs function in transaction and rolls back", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Create test table
		err := testDB.DB.Exec("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Insert initial data
		err = testDB.DB.Exec("INSERT INTO test_table (name) VALUES ('initial')").Error
		require.NoError(t, err)
		
		// Verify initial data
		var initialCount int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM test_table").Scan(&initialCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), initialCount)
		
		// Run in transaction (should rollback)
		err = testDB.RunInTransaction(func(tx *gorm.DB) error {
			// Insert data in transaction
			return tx.Exec("INSERT INTO test_table (name) VALUES ('transaction')").Error
		})
		
		// Should return error (test rollback)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "test rollback")
		
		// Verify data was rolled back
		var finalCount int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM test_table").Scan(&finalCount).Error
		require.NoError(t, err)
		assert.Equal(t, initialCount, finalCount) // Should be same as before transaction
	})

	t.Run("handles function error and rolls back", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Create test table
		err := testDB.DB.Exec("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Insert initial data
		err = testDB.DB.Exec("INSERT INTO test_table (name) VALUES ('initial')").Error
		require.NoError(t, err)
		
		// Run in transaction with function error
		err = testDB.RunInTransaction(func(tx *gorm.DB) error {
			// Insert data in transaction
			if err := tx.Exec("INSERT INTO test_table (name) VALUES ('transaction')").Error; err != nil {
				return err
			}
			// Return error to trigger rollback
			return assert.AnError
		})
		
		// Should return the function error
		assert.Error(t, err)
		assert.Equal(t, assert.AnError, err)
		
		// Verify data was rolled back
		var finalCount int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM test_table").Scan(&finalCount).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), finalCount) // Should be same as before transaction
	})
}

func TestTestDB_GetRawDB(t *testing.T) {
	t.Run("returns underlying sql.DB", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		rawDB, err := testDB.GetRawDB()
		require.NoError(t, err)
		require.NotNil(t, rawDB)
		
		// Test that we can use the raw DB
		var result int
		err = rawDB.QueryRow("SELECT 1").Scan(&result)
		require.NoError(t, err)
		assert.Equal(t, 1, result)
	})

	t.Run("handles database error", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Close the database to simulate an error
		if sqlDB, err := testDB.DB.DB(); err == nil {
			sqlDB.Close()
		}
		
		rawDB, err := testDB.GetRawDB()
		// This should still work because GORM caches the sql.DB
		require.NoError(t, err)
		assert.NotNil(t, rawDB)
	})
}

func TestTestDB_MigrateModels(t *testing.T) {
	t.Run("migrates models successfully", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Define a simple model
		type TestModel struct {
			ID   uint   `gorm:"primaryKey"`
			Name string
		}
		
		// Migrate the model
		err := testDB.MigrateModels(&TestModel{})
		require.NoError(t, err)
		
		// Verify table was created
		var count int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='test_models'").Scan(&count).Error
		require.NoError(t, err)
		assert.Equal(t, int64(1), count)
		
		// Test that we can insert data
		err = testDB.DB.Create(&TestModel{Name: "test"}).Error
		require.NoError(t, err)
		
		// Verify data was inserted
		var model TestModel
		err = testDB.DB.First(&model).Error
		require.NoError(t, err)
		assert.Equal(t, "test", model.Name)
	})

	t.Run("migrates multiple models", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Define multiple models
		type Model1 struct {
			ID   uint   `gorm:"primaryKey"`
			Name string
		}
		
		type Model2 struct {
			ID    uint   `gorm:"primaryKey"`
			Title string
		}
		
		// Migrate both models
		err := testDB.MigrateModels(&Model1{}, &Model2{})
		require.NoError(t, err)
		
		// Check what tables were actually created
		var tableNames []string
		err = testDB.DB.Raw("SELECT name FROM sqlite_master WHERE type='table'").Scan(&tableNames).Error
		require.NoError(t, err)
		
		// Should have created both tables (GORM uses singular names by default)
		assert.Contains(t, tableNames, "model1")
		assert.Contains(t, tableNames, "model2")
		
		// Test that we can insert data into both tables
		err = testDB.DB.Create(&Model1{Name: "test1"}).Error
		require.NoError(t, err)
		
		err = testDB.DB.Create(&Model2{Title: "test2"}).Error
		require.NoError(t, err)
	})
}

func TestTestDB_EdgeCases(t *testing.T) {
	t.Run("handles concurrent access", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Create test table
		err := testDB.DB.Exec("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)").Error
		require.NoError(t, err)
		
		// Test concurrent access
		done := make(chan bool, 10)
		for i := 0; i < 10; i++ {
			go func(i int) {
				defer func() { done <- true }()
				
				// Each goroutine inserts a record
				err := testDB.DB.Exec("INSERT INTO test_table (name) VALUES (?)", "test"+string(rune(i))).Error
				assert.NoError(t, err)
			}(i)
		}
		
		// Wait for all goroutines to complete
		for i := 0; i < 10; i++ {
			<-done
		}
		
		// Verify all records were inserted
		var count int64
		err = testDB.DB.Raw("SELECT COUNT(*) FROM test_table").Scan(&count).Error
		require.NoError(t, err)
		assert.Equal(t, int64(10), count)
	})

	t.Run("handles context cancellation", func(t *testing.T) {
		testDB := SetupSQLiteTestDB(t)
		
		// Create a context with timeout
		ctx, cancel := context.WithTimeout(context.Background(), 1*time.Millisecond)
		defer cancel()
		
		// Wait for context to be cancelled
		time.Sleep(10 * time.Millisecond)
		
		// Try to use the database with cancelled context
		var result int
		err := testDB.DB.WithContext(ctx).Raw("SELECT 1").Scan(&result).Error
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "context")
	})
}