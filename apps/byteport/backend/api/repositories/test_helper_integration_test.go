//go:build integration

package repositories

import (
	"testing"

	"github.com/byteport/api/testhelpers"
)

func setupTestDB(t *testing.T) *testhelpers.TestDB {
	return testhelpers.SetupTestDB(t)
}
