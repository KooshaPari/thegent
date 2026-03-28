package store

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"

	"github.com/KooshaPari/pheno-session/internal/model"
)

// sqliteStore implements Store backed by SQLite.
type sqliteStore struct {
	db   *sql.DB
	path string
}

func NewSQLiteStore(path string) (Store, error) {
	if path == "" {
		home := os.Getenv("HOME")
		if home == "" {
			return nil, errors.New("HOME not set")
		}
		path = filepath.Join(home, ".local", "share", "phenotype", "sessions.db")
	}
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("create dir: %w", err)
	}

	db, err := sql.Open("sqlite3", path+"?_journal_mode=WAL&_busy_timeout=5000")
	if err != nil {
		return nil, fmt.Errorf("open sqlite: %w", err)
	}

	if _, err := db.Exec(SQLiteDDL); err != nil {
		db.Close()
		return nil, fmt.Errorf("apply ddl: %w", err)
	}

	return &sqliteStore{db: db, path: path}, nil
}

func (s *sqliteStore) UpsertSession(meta model.SessionMeta) error {
	if meta.ID == "" {
		meta.ID = fmt.Sprintf("sess-%d", time.Now().UnixNano())
	}
	if meta.CreatedAt.IsZero() {
		meta.CreatedAt = time.Now().UTC()
	}
	if meta.UpdatedAt.IsZero() {
		meta.UpdatedAt = time.Now().UTC()
	}
	metaBytes, _ := json.Marshal(meta.ProviderMeta)

	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	stmt := `INSERT INTO sessions (
  id, name, harness, provider, model, dir, created_at, updated_at, updated_by,
  last_message, state, provider_meta
 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                harness=excluded.harness,
                provider=excluded.provider,
                model=excluded.model,
                dir=excluded.dir,
                created_at=excluded.created_at,
                updated_at=excluded.updated_at,
                updated_by=excluded.updated_by,
                last_message=excluded.last_message,
                state=excluded.state,
                provider_meta=excluded.provider_meta;
        `
	_, err = tx.Exec(stmt,
		meta.ID, meta.Name, meta.Harness, meta.Provider, meta.Model, meta.Dir,
		meta.CreatedAt.UTC().Format(time.RFC3339Nano),
		meta.UpdatedAt.UTC().Format(time.RFC3339Nano),
		meta.UpdatedBy, meta.LastMessage, meta.State, string(metaBytes),
	)
	if err != nil {
		tx.Rollback()
		return err
	}
	return tx.Commit()
}

func (s *sqliteStore) GetSession(id string) (model.SessionMeta, error) {
	row := s.db.QueryRow(`SELECT id,name,harness,provider,model,dir,created_at,updated_at,updated_by,last_message,state,provider_meta FROM sessions WHERE id = ?`, id)
	var meta model.SessionMeta
	var createdAtStr, updatedAtStr, pmStr string
	if err := row.Scan(&meta.ID, &meta.Name, &meta.Harness, &meta.Provider, &meta.Model, &meta.Dir, &createdAtStr, &updatedAtStr, &meta.UpdatedBy, &meta.LastMessage, &meta.State, &pmStr); err != nil {
		if err == sql.ErrNoRows {
			return model.SessionMeta{}, errors.New("not found")
		}
		return model.SessionMeta{}, err
	}
	if t, err := time.Parse(time.RFC3339Nano, createdAtStr); err == nil {
		meta.CreatedAt = t
	}
	if t, err := time.Parse(time.RFC3339Nano, updatedAtStr); err == nil {
		meta.UpdatedAt = t
	}
	if pmStr != "" {
		_ = json.Unmarshal([]byte(pmStr), &meta.ProviderMeta)
	}
	return meta, nil
}

func (s *sqliteStore) ListSessions(filter SessionFilter) ([]model.SessionMeta, error) {
	builder := strings.Builder{}
	args := []any{}

	builder.WriteString("SELECT id,name,harness,provider,model,dir,created_at,updated_at,updated_by,last_message,state,provider_meta FROM sessions")
	whereAdded := false
	if filter.Harness != "" {
		if !whereAdded {
			builder.WriteString(" WHERE ")
			whereAdded = true
		} else {
			builder.WriteString(" AND ")
		}
		builder.WriteString("harness = ?")
		args = append(args, filter.Harness)
	}
	if !filter.All && filter.Dir != "" {
		if !whereAdded {
			builder.WriteString(" WHERE ")
			whereAdded = true
		} else {
			builder.WriteString(" AND ")
		}
		builder.WriteString("dir = ?")
		args = append(args, filter.Dir)
	}
	// Sorting
	switch filter.SortBy {
	case "updated_at":
		builder.WriteString(" ORDER BY updated_at DESC")
	case "name":
		builder.WriteString(" ORDER BY name ASC")
	default:
		// default: updated_by then updated_at desc (best-effort)
		builder.WriteString(" ORDER BY updated_by DESC, updated_at DESC")
	}
	if filter.Limit > 0 {
		builder.WriteString(fmt.Sprintf(" LIMIT %d", filter.Limit))
	} else {
		builder.WriteString(" LIMIT 100")
	}

	rows, err := s.db.Query(builder.String(), args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := []model.SessionMeta{}
	for rows.Next() {
		var meta model.SessionMeta
		var createdAtStr, updatedAtStr, pmStr string
		if err := rows.Scan(&meta.ID, &meta.Name, &meta.Harness, &meta.Provider, &meta.Model, &meta.Dir, &createdAtStr, &updatedAtStr, &meta.UpdatedBy, &meta.LastMessage, &meta.State, &pmStr); err != nil {
			return nil, err
		}
		if t, err := time.Parse(time.RFC3339Nano, createdAtStr); err == nil {
			meta.CreatedAt = t
		}
		if t, err := time.Parse(time.RFC3339Nano, updatedAtStr); err == nil {
			meta.UpdatedAt = t
		}
		if pmStr != "" {
			_ = json.Unmarshal([]byte(pmStr), &meta.ProviderMeta)
		}
		out = append(out, meta)
	}
	return out, nil
}

func (s *sqliteStore) DeleteSession(id string) error {
	_, err := s.db.Exec("DELETE FROM sessions WHERE id = ?", id)
	return err
}
