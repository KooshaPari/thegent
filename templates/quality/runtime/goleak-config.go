// goleak — Goroutine leak detection for Go tests
// Install: go get go.uber.org/goleak
//
// Usage: Add to TestMain to detect goroutine leaks across all tests.
// Any goroutine still running after tests complete (that wasn't running before)
// is reported as a leak.
//
// Options:
//   goleak.IgnoreTopFunction("...") — ignore specific goroutines
//   goleak.IgnoreCurrent()          — ignore goroutines running at start

package main_test

import (
	"os"
	"testing"

	"go.uber.org/goleak"
)

func TestMain(m *testing.M) {
	// Verify no goroutine leaks after all tests complete
	goleak.VerifyTestMain(m,
		// Common goroutines to ignore:
		// goleak.IgnoreTopFunction("net/http.(*Server).Serve"),
		// goleak.IgnoreTopFunction("database/sql.(*DB).connectionOpener"),
	)
	os.Exit(m.Run())
}

// Per-test leak detection (alternative to TestMain):
// func TestSomething(t *testing.T) {
//     defer goleak.VerifyNone(t)
//     // ... test code ...
// }
