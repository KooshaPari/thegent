package store

import (
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/KooshaPari/pheno-session/internal/model"
)

func TestJSONStoreUpsertGetListDelete(t *testing.T) {
	tmp := t.TempDir()
	p := filepath.Join(tmp, "sessions.json")
	s, err := NewJSONStore(p)
	if err != nil {
		t.Fatalf("NewJSONStore: %v", err)
	}
	meta := model.SessionMeta{
		ID:          "sess-1",
		Name:        "test",
		Harness:     "forge",
		Provider:    "forge",
		Model:       "gpt-4o",
		Dir:         "/tmp",
		CreatedAt:   time.Now().UTC(),
		UpdatedAt:   time.Now().UTC(),
		UpdatedBy:   "user",
		LastMessage: "hello",
		State:       "active",
	}
	if err := s.UpsertSession(meta); err != nil {
		t.Fatalf("Upsert: %v", err)
	}
	got, err := s.GetSession("sess-1")
	if err != nil {
		t.Fatalf("GetSession: %v", err)
	}
	if got.Name != "test" {
		t.Fatalf("expected name test; got %s", got.Name)
	}
	list, err := s.ListSessions(SessionFilter{All: true})
	if err != nil {
		t.Fatalf("ListSessions: %v", err)
	}
	if len(list) != 1 {
		t.Fatalf("expected 1; got %d", len(list))
	}
	if err := s.DeleteSession("sess-1"); err != nil {
		t.Fatalf("DeleteSession: %v", err)
	}
	_, err = s.GetSession("sess-1")
	if err == nil {
		t.Fatalf("expected not found after delete")
	}
	// ensure file written
	if _, err := os.Stat(p); err != nil {
		t.Fatalf("expected file exists: %v", err)
	}
}
