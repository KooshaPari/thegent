package store

import "github.com/KooshaPari/pheno-session/internal/model"

// SessionFilter used for listing sessions (shared shape with adapter)
type SessionFilter struct {
	Harness  string
	Provider string
	Dir      string
	All      bool
	SortBy   string
	Limit    int
	Offset   int
}

type Store interface {
	UpsertSession(model.SessionMeta) error
	GetSession(id string) (model.SessionMeta, error)
	ListSessions(filter SessionFilter) ([]model.SessionMeta, error)
	DeleteSession(id string) error
}
