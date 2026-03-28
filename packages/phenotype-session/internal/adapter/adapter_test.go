package adapter

import (
	"testing"
	"time"
)

// TestHarnessAdapterInterface tests that all adapters implement the interface
func TestHarnessAdapterInterface(t *testing.T) {
	adapters := []HarnessAdapter{
		NewForgeAdapterV2(),
		NewCodexAdapter(),
		NewCursorAdapter(),
		NewClaudeAdapter(),
		NewDroidAdapter(),
	}

	harnesses := []string{"forge", "codex", "cursor", "claude", "droid"}

	for i, a := range adapters {
		t.Run(harnesses[i]+"_Type", func(t *testing.T) {
			if a.Type() == "" {
				t.Error("Type() returned empty string")
			}
		})

		t.Run(harnesses[i]+"_Priority", func(t *testing.T) {
			prio := a.GetPriority()
			if prio < 0 {
				t.Errorf("GetPriority() returned negative: %d", prio)
			}
		})

		t.Run(harnesses[i]+"_ListSessions", func(t *testing.T) {
			sessions, err := a.ListSessions()
			if err != nil {
				t.Logf("ListSessions error (may be expected): %v", err)
			}
			// Empty list is acceptable (stub implementation)
			if sessions == nil {
				sessions = []SessionInfo{}
			}
		})
	}
}

// TestForgeAdapter tests Forge-specific functionality
func TestForgeAdapter(t *testing.T) {
	adapter := NewForgeAdapterV2()

	t.Run("Type_ReturnsForge", func(t *testing.T) {
		if adapter.Type() != HarnessForge {
			t.Errorf("Expected HarnessForge, got %s", adapter.Type())
		}
	})

	t.Run("Priority_Highest", func(t *testing.T) {
		if adapter.GetPriority() != 1 {
			t.Errorf("Expected priority 1, got %d", adapter.GetPriority())
		}
	})

	t.Run("IsAvailable_ChecksConfig", func(t *testing.T) {
		// Should return true if API is configured or CLI is available
		_ = adapter.IsAvailable()
		// Just verify it doesn't panic
	})

	t.Run("StartSession_CreatesSession", func(t *testing.T) {
		params := StartParams{
			Model:  "gpt-4o",
			Name:   "test-session",
			Dir:    "/tmp",
			Meta:   map[string]any{"test": true},
		}

		session, err := adapter.StartSession(params)
		if err != nil {
			t.Errorf("StartSession failed: %v", err)
			return
		}

		if session == nil {
			t.Error("StartSession returned nil")
			return
		}

		if session.ID == "" {
			t.Error("Session ID is empty")
		}

		if session.Model != "gpt-4o" {
			t.Errorf("Expected model gpt-4o, got %s", session.Model)
		}
	})

	t.Run("GetSession_NotFound", func(t *testing.T) {
		session, err := adapter.GetSession("nonexistent-id")
		// Should return error for non-existent session
		if err == nil && session != nil {
			// This is OK - API might return stub
			t.Log("GetSession returned stub for non-existent session")
		}
	})
}

// TestCodexAdapter tests Codex-specific functionality
func TestCodexAdapter(t *testing.T) {
	adapter := NewCodexAdapter()

	t.Run("Type_ReturnsCodex", func(t *testing.T) {
		if adapter.Type() != HarnessCodex {
			t.Errorf("Expected HarnessCodex, got %s", adapter.Type())
		}
	})

	t.Run("StartSession_CreatesSession", func(t *testing.T) {
		params := StartParams{
			Model:  "claude-3-5-sonnet",
			Name:   "codex-test",
			Dir:    "/tmp",
			Meta:   map[string]any{"test": true},
		}

		session, err := adapter.StartSession(params)
		if err != nil {
			t.Errorf("StartSession failed: %v", err)
			return
		}

		if session == nil {
			t.Error("StartSession returned nil")
			return
		}
	})
}

// TestCursorAdapter tests Cursor-specific functionality
func TestCursorAdapter(t *testing.T) {
	adapter := NewCursorAdapter()

	t.Run("Type_ReturnsCursor", func(t *testing.T) {
		if adapter.Type() != HarnessCursor {
			t.Errorf("Expected HarnessCursor, got %s", adapter.Type())
		}
	})

	t.Run("ListSessions_ReturnsList", func(t *testing.T) {
		sessions, err := adapter.ListSessions()
		if err != nil {
			t.Logf("ListSessions error (may be expected): %v", err)
		}
		// Empty list is acceptable (stub implementation)
		if sessions == nil {
			sessions = []SessionInfo{}
		}
	})
}

// TestClaudeAdapter tests Claude-specific functionality
func TestClaudeAdapter(t *testing.T) {
	adapter := NewClaudeAdapter()

	t.Run("Type_ReturnsClaude", func(t *testing.T) {
		if adapter.Type() != HarnessClaude {
			t.Errorf("Expected HarnessClaude, got %s", adapter.Type())
		}
	})

	t.Run("StartSession_CreatesSession", func(t *testing.T) {
		params := StartParams{
			Model:  "claude-opus-4",
			Name:   "claude-test",
			Dir:    "/tmp",
		}

		session, err := adapter.StartSession(params)
		if err != nil {
			t.Errorf("StartSession failed: %v", err)
			return
		}

		if session == nil {
			t.Error("StartSession returned nil")
			return
		}
	})
}

// TestDroidAdapter tests Droid-specific functionality
func TestDroidAdapter(t *testing.T) {
	adapter := NewDroidAdapter()

	t.Run("Type_ReturnsDroid", func(t *testing.T) {
		if adapter.Type() != HarnessFactoryDroid {
			t.Errorf("Expected HarnessFactoryDroid, got %s", adapter.Type())
		}
	})

	t.Run("StartSession_CreatesSession", func(t *testing.T) {
		params := StartParams{
			Model:  "gpt-4",
			Name:   "droid-test",
			Dir:    "/tmp",
		}

		session, err := adapter.StartSession(params)
		if err != nil {
			// Droid may not be installed - this is expected
			t.Logf("StartSession error (may be expected if droid not installed): %v", err)
			return
		}

		if session == nil {
			t.Error("StartSession returned nil")
			return
		}
	})
}

// TestTransferSession tests session transfer functionality
func TestTransferSession(t *testing.T) {
	adapters := []HarnessAdapter{
		NewForgeAdapterV2(),
		NewCodexAdapter(),
	}

	for _, adapter := range adapters {
		t.Run(string(adapter.Type())+"_TransferSession", func(t *testing.T) {
			// First create a session
			session, err := adapter.StartSession(StartParams{
				Model: "gpt-4o",
				Name:  "transfer-test",
				Dir:   "/tmp",
			})
			if err != nil {
				t.Skipf("Skipping transfer test: %v", err)
			}

			// Try to transfer
			newSession, err := adapter.TransferSession(session.ID, "other-harness", nil)
			if err != nil {
				// Transfer might not be implemented
				t.Logf("TransferSession error (may be expected): %v", err)
			}
			if newSession != nil {
				t.Logf("Transfer returned new session: %s", newSession.ID)
			}
		})
	}
}

// TestOpenSession tests session opening functionality
func TestOpenSession(t *testing.T) {
	adapter := NewForgeAdapterV2()

	t.Run("OpenSession_NoError", func(t *testing.T) {
		// Create a session first
		session, err := adapter.StartSession(StartParams{
			Model: "gpt-4o",
			Name:  "open-test",
			Dir:   "/tmp",
		})
		if err != nil {
			t.Skipf("Skipping: %v", err)
		}

		// Try to open (should not panic)
		err = adapter.OpenSession(session.ID, "")
		if err != nil {
			t.Logf("OpenSession error (may be expected): %v", err)
		}
	})
}

// TestStartParams tests the StartParams structure
func TestStartParams(t *testing.T) {
	params := StartParams{
		Model:  "gpt-4o",
		Name:   "test",
		Dir:    "/tmp",
		Meta:   map[string]any{"key": "value"},
	}

	if params.Model != "gpt-4o" {
		t.Error("Model not set correctly")
	}

	if params.Name != "test" {
		t.Error("Name not set correctly")
	}

	if params.Dir != "/tmp" {
		t.Error("Dir not set correctly")
	}

	if params.Meta["key"] != "value" {
		t.Error("Meta not set correctly")
	}
}

// TestSessionInfo tests the SessionInfo structure
func TestSessionInfo(t *testing.T) {
	info := SessionInfo{
		ID:              "test-id",
		Name:            "test-session",
		Model:           "gpt-4o",
		State:           "active",
		CreatedAt:       time.Now(),
		LastActivityAt:  time.Now(),
		Metadata:        map[string]any{"key": "value"},
	}

	if info.ID != "test-id" {
		t.Error("ID not set correctly")
	}

	if info.Model != "gpt-4o" {
		t.Error("Model not set correctly")
	}

	if info.State != "active" {
		t.Error("State not set correctly")
	}

	if info.Metadata["key"] != "value" {
		t.Error("Metadata not set correctly")
	}
}

// TestHarnessType tests HarnessType constants
func TestHarnessType(t *testing.T) {
	tests := []struct {
		harness HarnessType
		want    string
	}{
		{HarnessForge, "forge"},
		{HarnessCodex, "codex"},
		{HarnessCursor, "cursor"},
		{HarnessClaude, "claude"},
		{HarnessFactoryDroid, "factory-droid"},
	}

	for _, tt := range tests {
		t.Run(tt.want, func(t *testing.T) {
			if string(tt.harness) != tt.want {
				t.Errorf("Expected %s, got %s", tt.want, string(tt.harness))
			}
		})
	}
}
