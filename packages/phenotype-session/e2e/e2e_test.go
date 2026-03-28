package e2e

import (
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/KooshaPari/phenotype-session/internal/adapter"
	"github.com/KooshaPari/phenotype-session/internal/sqlite"
	"github.com/KooshaPari/phenotype-session/internal/transfer"
)

// TestHelper provides test utilities
type TestHelper struct {
	Store       *sqlite.UnifiedStore
	TransferMgr *transfer.TransferManager
	TempDir     string
}

func NewTestHelper(t *testing.T) *TestHelper {
	// Create temp directory for test db
	tempDir, err := os.MkdirTemp("", "pheno-e2e-*")
	if err != nil {
		t.Fatalf("failed to create temp dir: %v", err)
	}

	dbPath := filepath.Join(tempDir, "test.db")
	store, err := sqlite.NewUnifiedStore(dbPath)
	if err != nil {
		os.RemoveAll(tempDir)
		t.Fatalf("failed to create store: %v", err)
	}

	tm := transfer.NewTransferManager(store)
	for _, h := range []adapter.HarnessType{
		adapter.HarnessForge,
		adapter.HarnessCodex,
		adapter.HarnessCursor,
		adapter.HarnessClaude,
	} {
		tm.RegisterAdapter(string(h), adapter.NewAdapter(h))
	}

	return &TestHelper{
		Store:       store,
		TransferMgr: tm,
		TempDir:     tempDir,
	}
}

func (h *TestHelper) Cleanup() {
	h.Store.Close()
	os.RemoveAll(h.TempDir)
}

// TestE2ESessionLifecycle tests complete session lifecycle
func TestE2ESessionLifecycle(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	// 1. Create session
	session := sqlite.Session{
		ID:              "test-session-1",
		Harness:         "forge",
		Provider:        "forge",
		Model:           "gpt-4o",
		ProjectPath:     "/tmp/test",
		State:           "active",
		StartedAt:       time.Now(),
		LastActivityAt:  time.Now(),
		Summary:         "Test session",
	}
	if err := h.Store.CreateSession(session); err != nil {
		t.Fatalf("CreateSession failed: %v", err)
	}

	// 2. List sessions
	sessions, err := h.Store.ListSessions(sqlite.SessionFilter{Limit: 10})
	if err != nil {
		t.Fatalf("ListSessions failed: %v", err)
	}
	if len(sessions) != 1 {
		t.Errorf("expected 1 session, got %d", len(sessions))
	}

	// 3. Get session
	retrieved, err := h.Store.GetSession("test-session-1")
	if err != nil {
		t.Fatalf("GetSession failed: %v", err)
	}
	if retrieved.Harness != "forge" {
		t.Errorf("expected harness forge, got %s", retrieved.Harness)
	}

	t.Log("✓ Session lifecycle test passed")
}

// TestE2EAdapterRegistry tests adapter registration
func TestE2EAdapterRegistry(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	harnesses := []string{"forge", "codex", "cursor", "claude"}
	for _, hName := range harnesses {
		a := h.TransferMgr.GetAdapter(hName)
		if a == nil {
			t.Errorf("adapter for %s should not be nil", hName)
		} else {
			t.Logf("✓ Registered adapter for %s: %v", hName, a.Type())
		}
	}
}

// TestE2ETransferWorkflow tests session transfer between harnesses
func TestE2ETransferWorkflow(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	// 1. Create source session
	session := sqlite.Session{
		ID:             "transfer-source",
		Harness:        "forge",
		Provider:       "forge",
		Model:          "gpt-4o",
		ProjectPath:    "/tmp/test",
		State:          "active",
		StartedAt:      time.Now(),
		LastActivityAt: time.Now(),
		Summary:        "Source session for transfer",
	}
	_ = h.Store.CreateSession(session)

	// 2. Create snapshot
	snapshot, err := h.TransferMgr.CreateSnapshot("transfer-source")
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}
	if snapshot.Harness != "forge" {
		t.Errorf("expected harness forge, got %s", snapshot.Harness)
	}
	if snapshot.Model != "gpt-4o" {
		t.Errorf("expected model gpt-4o, got %s", snapshot.Model)
	}

	// 3. Export snapshot
	snapshotJSON, err := h.TransferMgr.ExportSnapshot("transfer-source")
	if err != nil {
		t.Fatalf("ExportSnapshot failed: %v", err)
	}
	if len(snapshotJSON) == 0 {
		t.Error("snapshot JSON is empty")
	}

	// 4. Verify source session still exists
	_, err = h.Store.GetSession("transfer-source")
	if err != nil {
		t.Errorf("source session should still exist: %v", err)
	}

	t.Log("✓ Transfer workflow test passed")
}

// TestE2EConcurrentAccess tests concurrent store access
func TestE2EConcurrentAccess(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	done := make(chan bool, 5)

	// Concurrent session creates
	for i := 0; i < 5; i++ {
		go func(id int) {
			session := sqlite.Session{
				ID:             "concurrent-session-" + string(rune('0'+id)),
				Harness:        "forge",
				Provider:       "forge",
				Model:          "gpt-4o",
				State:          "active",
				StartedAt:      time.Now(),
				LastActivityAt: time.Now(),
			}
			_ = h.Store.CreateSession(session)
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 5; i++ {
		<-done
	}

	// Verify all sessions created
	sessions, _ := h.Store.ListSessions(sqlite.SessionFilter{Limit: 100})
	if len(sessions) < 5 {
		t.Errorf("expected at least 5 sessions, got %d", len(sessions))
	}

	t.Log("✓ Concurrent access test passed")
}

// TestE2EFullSitbackAudit tests full audit report generation
func TestE2EFullSitbackAudit(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	// Setup: Create sessions across harnesses
	harnesses := []string{"forge", "codex", "cursor", "claude"}
	for i, hName := range harnesses {
		session := sqlite.Session{
			ID:             "audit-full-" + hName,
			Harness:        hName,
			Provider:       hName,
			Model:          "gpt-4o",
			State:          "active",
			StartedAt:      time.Now().Add(-time.Duration(i) * time.Hour),
			LastActivityAt: time.Now(),
		}
		_ = h.Store.CreateSession(session)
	}

	// Query for audit report
	sessions, _ := h.Store.ListSessions(sqlite.SessionFilter{Limit: 100})

	// Verify counts
	if len(sessions) != len(harnesses) {
		t.Errorf("expected %d sessions, got %d", len(harnesses), len(sessions))
	}

	// Count by harness
	harnessCounts := make(map[string]int)
	for _, s := range sessions {
		harnessCounts[s.Harness]++
	}

	// Count by state
	stateCounts := make(map[string]int)
	for _, s := range sessions {
		stateCounts[s.State]++
	}

	t.Logf("✓ Full sitback audit test passed:")
	t.Logf("  - Sessions by harness: %v", harnessCounts)
	t.Logf("  - Sessions by state: %v", stateCounts)
}

// TestE2EAdapterInterface tests all adapters implement interface
func TestE2EAdapterInterface(t *testing.T) {
	adapters := []adapter.HarnessAdapter{
		adapter.NewAdapter(adapter.HarnessForge),
		adapter.NewAdapter(adapter.HarnessCodex),
		adapter.NewAdapter(adapter.HarnessCursor),
		adapter.NewAdapter(adapter.HarnessClaude),
	}

	for _, a := range adapters {
		// Test Type
		harnessType := a.Type()
		t.Logf("✓ Adapter %v has type: %v", a, harnessType)

		// Test Priority
		priority := a.GetPriority()
		if priority < 1 {
			t.Errorf("invalid priority: %d", priority)
		}

		// Test IsAvailable
		_ = a.IsAvailable()

		// Test ListSessions
		_, _ = a.ListSessions()
	}

	t.Log("✓ All adapters implement interface correctly")
}

// TestE2ESnapshotExport tests snapshot export functionality
func TestE2ESnapshotExport(t *testing.T) {
	h := NewTestHelper(t)
	defer h.Cleanup()

	// Create session
	session := sqlite.Session{
		ID:             "snapshot-test",
		Harness:        "codex",
		Provider:       "codex",
		Model:          "gpt-4o",
		State:          "active",
		StartedAt:      time.Now(),
		LastActivityAt: time.Now(),
	}
	_ = h.Store.CreateSession(session)

	// Export snapshot
	jsonData, err := h.TransferMgr.ExportSnapshot("snapshot-test")
	if err != nil {
		t.Fatalf("ExportSnapshot failed: %v", err)
	}

	if len(jsonData) == 0 {
		t.Error("exported JSON is empty")
	}

	t.Logf("✓ Snapshot export works, exported %d bytes", len(jsonData))
}
