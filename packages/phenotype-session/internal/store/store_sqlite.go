package store

// Note: this file provides helper DDL and placeholder for SQLite-backed store.
// Full implementation would use database/sql and a driver such as github.com/mattn/go-sqlite3

const SQLiteDDL = `
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  name TEXT,
  harness TEXT,
  provider TEXT,
  model TEXT,
  dir TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  updated_by TEXT,
  last_message TEXT,
  state TEXT,
  provider_meta JSON
);
CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_updated_by ON sessions(updated_by);
CREATE INDEX IF NOT EXISTS idx_sessions_harness ON sessions(harness);
`

// Full SQLite implementation will be added in sqlite_store_impl.go
