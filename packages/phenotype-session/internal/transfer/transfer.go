package transfer

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/KooshaPari/phenotype-session/internal/adapter"
	"github.com/KooshaPari/phenotype-session/internal/sqlite"
)

// Snapshot represents a portable session snapshot
type Snapshot struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	Harness       string                 `json:"harness"`
	Provider      string                 `json:"provider"`
	Model         string                 `json:"model"`
	ProjectPath   string                 `json:"project_path"`
	State         string                 `json:"state"`
	CreatedAt     time.Time              `json:"created_at"`
	LastActivity  time.Time              `json:"last_activity"`
	Messages      []MessageSnapshot       `json:"messages,omitempty"`
	FilesModified []FileSnapshot          `json:"files_modified,omitempty"`
	Context       map[string]interface{}  `json:"context,omitempty"`
	Metadata      map[string]interface{}  `json:"metadata"`
}

// MessageSnapshot represents a message in the session
type MessageSnapshot struct {
	Role      string    `json:"role"`
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
}

// FileSnapshot represents a modified file
type FileSnapshot struct {
	Path      string `json:"path"`
	ChangeType string `json:"change_type"` // created, modified, deleted
	Diff      string `json:"diff,omitempty"`
}

// TransferManager handles session transfers between harnesses
type TransferManager struct {
	store     *sqlite.UnifiedStore
	adapters  map[string]adapter.HarnessAdapter
}

// NewTransferManager creates a new transfer manager
func NewTransferManager(store *sqlite.UnifiedStore) *TransferManager {
	return &TransferManager{
		store:    store,
		adapters: make(map[string]adapter.HarnessAdapter),
	}
}

// GetAdapter returns a registered adapter
func (tm *TransferManager) GetAdapter(harness string) adapter.HarnessAdapter {
	return tm.adapters[harness]
}

// RegisterAdapter registers a harness adapter for transfers
func (tm *TransferManager) RegisterAdapter(harness string, a adapter.HarnessAdapter) {
	tm.adapters[harness] = a
}

// CreateSnapshot creates a portable snapshot of a session
func (tm *TransferManager) CreateSnapshot(sessionID string) (*Snapshot, error) {
	session, err := tm.store.GetSession(sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get session: %w", err)
	}

	// Create basic snapshot
	snapshot := &Snapshot{
		ID:           session.ID,
		Name:         session.Summary, // Use Summary as Name
		Harness:      session.Harness,
		Provider:     session.Provider,
		Model:        session.Model,
		ProjectPath:  session.ProjectPath,
		State:        session.State,
		CreatedAt:    session.StartedAt,
		LastActivity: session.LastActivityAt,
		Metadata:     make(map[string]interface{}),
	}

	// Get session history if adapter is available
	if a, ok := tm.adapters[session.Harness]; ok {
		// Try to get messages from adapter
		if msgs, err := a.GetSessionMessages(sessionID); err == nil {
			// Convert adapter.MessageSnapshot to local MessageSnapshot
			for _, m := range msgs {
				snapshot.Messages = append(snapshot.Messages, MessageSnapshot{
					Role:      m.Role,
					Content:   m.Content,
					Timestamp: m.Timestamp,
				})
			}
		}
	}

	return snapshot, nil
}

// Transfer transfers a session to a new harness
func (tm *TransferManager) Transfer(sessionID, targetHarness string, params TransferParams) (*sqlite.Session, error) {
	// Create snapshot of source session
	snapshot, err := tm.CreateSnapshot(sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to create snapshot: %w", err)
	}

	// Get target adapter
	targetAdapter, ok := tm.adapters[targetHarness]
	if !ok {
		return nil, fmt.Errorf("unknown harness: %s", targetHarness)
	}

	// Start new session in target harness
	sessionInfo, err := targetAdapter.StartSession(adapter.StartParams{
		Model:    snapshot.Model,
		Name:     snapshot.Name,
		Provider: targetHarness,
		Dir:      snapshot.ProjectPath,
		Meta:     snapshot.Metadata,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to start session in target harness: %w", err)
	}

	// Create new session in store
	newSession := sqlite.Session{
		ID:             sessionInfo.ID,
		Summary:        snapshot.Name, // Use Name as Summary
		Harness:        targetHarness,
		Provider:       targetHarness,
		Model:          snapshot.Model,
		ProjectPath:    snapshot.ProjectPath,
		State:          "active",
		StartedAt:      time.Now(),
		LastActivityAt: time.Now(),
	}

	if err := tm.store.CreateSession(newSession); err != nil {
		return nil, fmt.Errorf("failed to create session in store: %w", err)
	}

	// Record transfer in audit log
	auditEntry := sqlite.AuditLogEntry{
		AuditID:    fmt.Sprintf("transfer-%d", time.Now().UnixNano()),
		Timestamp:  time.Now(),
		EventType:  "session_transfer",
		DetailsJSON: marshalTransferDetails(sessionID, targetHarness, snapshot),
	}
	_ = tm.store.CreateAuditEntry(auditEntry)

	return &newSession, nil
}

// TransferParams contains parameters for transfer
type TransferParams struct {
	PreserveHistory bool
	IncludeFiles    bool
	Priority        int
}

// ExportSnapshot exports a snapshot to JSON
func (tm *TransferManager) ExportSnapshot(sessionID string) ([]byte, error) {
	snapshot, err := tm.CreateSnapshot(sessionID)
	if err != nil {
		return nil, err
	}
	return json.MarshalIndent(snapshot, "", "  ")
}

// ImportSnapshot imports a snapshot and creates a session
func (tm *TransferManager) ImportSnapshot(data []byte, targetHarness string) (*sqlite.Session, error) {
	var snapshot Snapshot
	if err := json.Unmarshal(data, &snapshot); err != nil {
		return nil, fmt.Errorf("failed to parse snapshot: %w", err)
	}

	targetAdapter, ok := tm.adapters[targetHarness]
	if !ok {
		return nil, fmt.Errorf("unknown harness: %s", targetHarness)
	}

	sessionInfo, err := targetAdapter.StartSession(adapter.StartParams{
		Model:    snapshot.Model,
		Name:    snapshot.Name,
		Provider: targetHarness,
		Dir:     snapshot.ProjectPath,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to start session: %w", err)
	}

	newSession := sqlite.Session{
		ID:             sessionInfo.ID,
		Summary:        snapshot.Name,
		Harness:        targetHarness,
		Provider:       targetHarness,
		Model:          snapshot.Model,
		ProjectPath:    snapshot.ProjectPath,
		State:          "active",
		StartedAt:      time.Now(),
		LastActivityAt: time.Now(),
	}

	if err := tm.store.CreateSession(newSession); err != nil {
		return nil, fmt.Errorf("failed to create session: %w", err)
	}

	return &newSession, nil
}

// helper
func marshalTransferDetails(fromID, toHarness string, snapshot *Snapshot) string {
	details := map[string]interface{}{
		"from_session": fromID,
		"to_harness":   toHarness,
		"snapshot":      snapshot,
	}
	data, _ := json.Marshal(details)
	return string(data)
}
