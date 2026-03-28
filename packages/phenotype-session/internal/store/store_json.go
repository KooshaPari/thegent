package store

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/google/uuid"

	"github.com/KooshaPari/phenotype-session/internal/model"
)

const defaultJSONPath = ".local/share/phenotype/sessions.json"

type jsonStore struct {
	path string
	mu   sync.Mutex
	data map[string]model.SessionMeta
}

func NewJSONStore(path string) (Store, error) {
	if path == "" {
		home := os.Getenv("HOME")
		if home == "" {
			return nil, errors.New("HOME not set")
		}
		path = filepath.Join(home, defaultJSONPath)
	}
	s := &jsonStore{
		path: path,
		data: map[string]model.SessionMeta{},
	}
	_ = s.load()
	return s, nil
}

func (s *jsonStore) load() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	f, err := os.Open(s.path)
	if err != nil {
		if os.IsNotExist(err) {
			s.data = map[string]model.SessionMeta{}
			return nil
		}
		return err
	}
	defer f.Close()
	dec := json.NewDecoder(f)
	var arr []model.SessionMeta
	if err := dec.Decode(&arr); err != nil {
		return err
	}
	for _, m := range arr {
		s.data[m.ID] = m
	}
	return nil
}

func (s *jsonStore) persist() error {
	// Note: caller must hold s.mu.Lock()
	dir := filepath.Dir(s.path)
	_ = os.MkdirAll(dir, 0o755)
	f, err := os.Create(s.path)
	if err != nil {
		return err
	}
	defer f.Close()
	arr := make([]model.SessionMeta, 0, len(s.data))
	for _, v := range s.data {
		arr = append(arr, v)
	}
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	return enc.Encode(arr)
}

func (s *jsonStore) UpsertSession(meta model.SessionMeta) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if meta.ID == "" {
		meta.ID = uuid.New().String()
	}
	if meta.UpdatedAt.IsZero() {
		meta.UpdatedAt = time.Now().UTC()
	}
	s.data[meta.ID] = meta
	return s.persist()
}

func (s *jsonStore) GetSession(id string) (model.SessionMeta, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	m, ok := s.data[id]
	if !ok {
		return model.SessionMeta{}, errors.New("not found")
	}
	return m, nil
}

func (s *jsonStore) ListSessions(filter SessionFilter) ([]model.SessionMeta, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]model.SessionMeta, 0, len(s.data))
	for _, v := range s.data {
		if filter.Harness != "" && v.Harness != filter.Harness {
			continue
		}
		if !filter.All && filter.Dir != "" && v.Dir != filter.Dir {
			continue
		}
		out = append(out, v)
	}
	// For prototype, no sorting implemented; return up to Limit
	limit := filter.Limit
	if limit <= 0 || limit > len(out) {
		limit = len(out)
	}
	return out[:limit], nil
}

func (s *jsonStore) DeleteSession(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.data, id)
	return s.persist()
}
