package sqlite

import (
	"database/sql"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// UnifiedStore implements all storage operations for the unified session orchestration system
type UnifiedStore struct {
	db   *sql.DB
	path string
}

// Session represents a session in the unified store
type Session struct {
	ID              string    `json:"id"`
	Harness         string    `json:"harness"`
	Provider        string    `json:"provider"`
	Model           string    `json:"model"`
	ProjectPath     string    `json:"project_path"`
	WorkingDir      string    `json:"working_directory"`
	State           string    `json:"state"`
	StartedAt       time.Time `json:"started_at"`
	EndedAt         time.Time `json:"ended_at"`
	LastActivityAt  time.Time `json:"last_activity_at"`
	PromptTokens    int       `json:"prompt_tokens"`
	CompletionTokens int      `json:"completion_tokens"`
	CostUSD         float64   `json:"cost_usd"`
	MessagesJSON    string    `json:"messages_json"`
	Summary         string    `json:"summary"`
	GoalsJSON       string    `json:"goals_json"`
	ArtifactsJSON   string    `json:"artifacts_json"`
	TeamID          string    `json:"team_id"`
	ParentSessionID string    `json:"parent_session_id"`
	DelegationChainJSON string `json:"delegation_chain_json"`
	CompletionState string    `json:"completion_state"`
	ResolutionNotes string    `json:"resolution_notes"`
	MetadataJSON    string    `json:"metadata_json"`
	IndexedAt       time.Time `json:"indexed_at"`
}

// RunningAgent represents a running agent
type RunningAgent struct {
	AgentID       string    `json:"agent_id"`
	Harness       string    `json:"harness"`
	SessionID     string    `json:"session_id"`
	PID           int       `json:"pid"`
	StartedAt     time.Time `json:"started_at"`
	LastHeartbeat time.Time `json:"last_heartbeat"`
	Status        string    `json:"status"`
	CurrentTask   string    `json:"current_task"`
	MetadataJSON  string    `json:"metadata_json"`
}

// AgentMessage represents inter-agent communication
type AgentMessage struct {
	MessageID       string    `json:"message_id"`
	FromAgent       string    `json:"from_agent"`
	ToAgent         string    `json:"to_agent"`
	SessionID       string    `json:"session_id"`
	MessageType     string    `json:"message_type"`
	PayloadJSON     string    `json:"payload_json"`
	Priority        int       `json:"priority"`
	SentAt          time.Time `json:"sent_at"`
	ReceivedAt      time.Time `json:"received_at"`
	Acknowledged    bool      `json:"acknowledged"`
	DeliveryStatus  string    `json:"delivery_status"`
}

// Task represents a task tracked across agents
type Task struct {
	TaskID        string    `json:"task_id"`
	SessionID     string    `json:"session_id"`
	TeamID        string    `json:"team_id"`
	Title         string    `json:"title"`
	Description   string    `json:"description"`
	Priority      int       `json:"priority"`
	State         string    `json:"state"`
	AssignedAgent string    `json:"assigned_agent"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
	StartedAt     time.Time `json:"started_at"`
	CompletedAt   time.Time `json:"completed_at"`
	ResultJSON    string    `json:"result_json"`
	ErrorMessage  string    `json:"error_message"`
}

// HarnessSync represents sync status for a harness
type HarnessSync struct {
	Harness        string    `json:"harness"`
	LastSyncAt     time.Time `json:"last_sync_at"`
	LastSessionAt  time.Time `json:"last_session_at"`
	SessionCount   int       `json:"session_count"`
	Status         string    `json:"status"`
	ErrorMessage   string    `json:"error_message"`
	MetadataJSON   string    `json:"metadata_json"`
}

// AuditLogEntry represents an audit log entry
type AuditLogEntry struct {
	AuditID    string    `json:"audit_id"`
	Timestamp  time.Time `json:"timestamp"`
	AgentID    string    `json:"agent_id"`
	SessionID  string    `json:"session_id"`
	EventType  string    `json:"event_type"`
	DetailsJSON string   `json:"details_json"`
}

// NewUnifiedStore creates a new unified SQLite store
func NewUnifiedStore(path string) (*UnifiedStore, error) {
	if path == "" {
		home := os.Getenv("HOME")
		if home == "" {
			return nil, errors.New("HOME not set")
		}
		path = filepath.Join(home, ".local", "share", "phenotype", "unified.db")
	}

	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("create dir: %w", err)
	}

	db, err := sql.Open("sqlite3", path+"?_journal_mode=WAL&_busy_timeout=5000")
	if err != nil {
		return nil, fmt.Errorf("open sqlite: %w", err)
	}

	// Apply schema
	if err := applySchema(db); err != nil {
		db.Close()
		return nil, fmt.Errorf("apply schema: %w", err)
	}

	return &UnifiedStore{db: db, path: path}, nil
}

// applySchema applies the unified schema to the database
func applySchema(db *sql.DB) error {
	// Read schema file
	schema, err := os.ReadFile(filepath.Join("internal", "sqlite", "schema.sql"))
	if err != nil {
		// Fallback: inline schema if file not found
		schema = []byte(getInlineSchema())
	}

	// Execute schema (split by semicolons)
	statements := splitStatements(string(schema))
	for _, stmt := range statements {
		stmt = trimComment(stmt)
		if stmt == "" {
			continue
		}
		if _, err := db.Exec(stmt); err != nil {
			// Ignore "table already exists" errors
			if !isExistsError(err) {
				return fmt.Errorf("exec statement: %w\nStatement: %s", err, stmt[:min(len(stmt), 100)])
			}
		}
	}
	return nil
}

func splitStatements(s string) []string {
	var statements []string
	var current strings.Builder
	inString := false
	
	for _, ch := range s {
		if ch == '\'' {
			inString = !inString
		}
		if ch == ';' && !inString {
			if current.Len() > 0 {
				statements = append(statements, strings.TrimSpace(current.String()))
				current.Reset()
			}
		} else {
			current.WriteRune(ch)
		}
	}
	
	if current.Len() > 0 {
		stmt := strings.TrimSpace(current.String())
		if stmt != "" {
			statements = append(statements, stmt)
		}
	}
	
	return statements
}

func trimComment(s string) string {
	// Remove leading comments
	s = strings.TrimSpace(s)
	if strings.HasPrefix(s, "--") {
		lines := strings.Split(s, "\n")
		var result []string
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			if !strings.HasPrefix(trimmed, "--") && trimmed != "" {
				result = append(result, line)
			}
		}
		s = strings.TrimSpace(strings.Join(result, "\n"))
	}
	return s
}

func isExistsError(err error) bool {
	if err == nil {
		return false
	}
	msg := err.Error()
	return strings.Contains(msg, "already exists") ||
		strings.Contains(msg, "duplicate") ||
		strings.Contains(msg, "UNIQUE constraint")
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// getInlineSchema returns the schema inline (fallback)
func getInlineSchema() string {
	return `
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    harness TEXT NOT NULL,
    provider TEXT,
    model TEXT,
    project_path TEXT,
    working_directory TEXT,
    state TEXT NOT NULL DEFAULT 'created',
    started_at TEXT NOT NULL,
    ended_at TEXT,
    last_activity_at TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    messages_json TEXT,
    summary TEXT,
    goals_json TEXT,
    artifacts_json TEXT,
    team_id TEXT,
    parent_session_id TEXT,
    delegation_chain_json TEXT,
    completion_state TEXT DEFAULT 'unknown',
    resolution_notes TEXT,
    metadata_json TEXT,
    indexed_at TEXT NOT NULL,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS running_agents (
    agent_id TEXT PRIMARY KEY,
    harness TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    pid INTEGER,
    started_at TEXT NOT NULL,
    last_heartbeat TEXT,
    status TEXT DEFAULT 'running',
    current_task TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS agent_messages (
    message_id TEXT PRIMARY KEY,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    message_type TEXT NOT NULL,
    payload_json TEXT,
    priority INTEGER DEFAULT 5,
    sent_at TEXT NOT NULL,
    received_at TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    delivery_status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(session_id),
    team_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    state TEXT DEFAULT 'pending',
    assigned_agent TEXT REFERENCES running_agents(agent_id),
    created_at TEXT NOT NULL,
    updated_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    result_json TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS harness_sync (
    harness TEXT PRIMARY KEY,
    last_sync_at TEXT NOT NULL,
    last_session_at TEXT,
    session_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ok',
    error_message TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    agent_id TEXT,
    session_id TEXT,
    event_type TEXT NOT NULL,
    details_json TEXT,
    FOREIGN KEY (agent_id) REFERENCES running_agents(agent_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);
`
}

// Close closes the database connection
func (s *UnifiedStore) Close() error {
	return s.db.Close()
}

// Session operations

// CreateSession creates a new session
func (s *UnifiedStore) CreateSession(session Session) error {
	query := `INSERT INTO sessions (
		session_id, harness, provider, model, project_path, working_directory,
		state, started_at, ended_at, last_activity_at,
		prompt_tokens, completion_tokens, cost_usd,
		messages_json, summary, goals_json, artifacts_json,
		team_id, parent_session_id, delegation_chain_json,
		completion_state, resolution_notes, metadata_json, indexed_at
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		session.ID, session.Harness, session.Provider, session.Model,
		session.ProjectPath, session.WorkingDir,
		session.State, session.StartedAt.Format(time.RFC3339Nano),
		nullTime(session.EndedAt), nullTime(session.LastActivityAt),
		session.PromptTokens, session.CompletionTokens, session.CostUSD,
		session.MessagesJSON, session.Summary, session.GoalsJSON, session.ArtifactsJSON,
		session.TeamID, session.ParentSessionID, session.DelegationChainJSON,
		session.CompletionState, session.ResolutionNotes, session.MetadataJSON,
		session.IndexedAt.Format(time.RFC3339Nano),
	)
	return err
}

// GetSession retrieves a session by ID
func (s *UnifiedStore) GetSession(id string) (*Session, error) {
	query := `SELECT session_id, harness, provider, model, project_path, working_directory,
		state, started_at, ended_at, last_activity_at,
		prompt_tokens, completion_tokens, cost_usd,
		messages_json, summary, goals_json, artifacts_json,
		team_id, parent_session_id, delegation_chain_json,
		completion_state, resolution_notes, metadata_json, indexed_at
	FROM sessions WHERE session_id = ?`

	row := s.db.QueryRow(query, id)
	return scanSession(row)
}

// ListSessions lists sessions with optional filters
func (s *UnifiedStore) ListSessions(filter SessionFilter) ([]Session, error) {
	query := `SELECT session_id, harness, provider, model, project_path, working_directory,
		state, started_at, ended_at, last_activity_at,
		prompt_tokens, completion_tokens, cost_usd,
		messages_json, summary, goals_json, artifacts_json,
		team_id, parent_session_id, delegation_chain_json,
		completion_state, resolution_notes, metadata_json, indexed_at
	FROM sessions WHERE 1=1`
	
	args := []interface{}{}
	
	if filter.Harness != "" {
		query += " AND harness = ?"
		args = append(args, filter.Harness)
	}
	if filter.State != "" {
		query += " AND state = ?"
		args = append(args, filter.State)
	}
	if filter.TeamID != "" {
		query += " AND team_id = ?"
		args = append(args, filter.TeamID)
	}
	if !filter.All && filter.WorkingDir != "" {
		query += " AND working_directory = ?"
		args = append(args, filter.WorkingDir)
	}
	
	switch filter.SortBy {
	case "started_at":
		query += " ORDER BY started_at DESC"
	case "last_activity":
		query += " ORDER BY last_activity_at DESC"
	case "completion_state":
		query += " ORDER BY completion_state"
	default:
		query += " ORDER BY started_at DESC"
	}
	
	if filter.Limit > 0 {
		query += fmt.Sprintf(" LIMIT %d", filter.Limit)
	} else {
		query += " LIMIT 100"
	}

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []Session
	for rows.Next() {
		s, err := scanSessionRows(rows)
		if err != nil {
			return nil, err
		}
		sessions = append(sessions, *s)
	}
	return sessions, nil
}

// UpdateSession updates an existing session
func (s *UnifiedStore) UpdateSession(session Session) error {
	query := `UPDATE sessions SET
		harness = ?, provider = ?, model = ?, project_path = ?, working_directory = ?,
		state = ?, ended_at = ?, last_activity_at = ?,
		prompt_tokens = ?, completion_tokens = ?, cost_usd = ?,
		messages_json = ?, summary = ?, goals_json = ?, artifacts_json = ?,
		team_id = ?, parent_session_id = ?, delegation_chain_json = ?,
		completion_state = ?, resolution_notes = ?, metadata_json = ?
	WHERE session_id = ?`

	_, err := s.db.Exec(query,
		session.Harness, session.Provider, session.Model, session.ProjectPath, session.WorkingDir,
		session.State, nullTime(session.EndedAt), nullTime(session.LastActivityAt),
		session.PromptTokens, session.CompletionTokens, session.CostUSD,
		session.MessagesJSON, session.Summary, session.GoalsJSON, session.ArtifactsJSON,
		session.TeamID, session.ParentSessionID, session.DelegationChainJSON,
		session.CompletionState, session.ResolutionNotes, session.MetadataJSON,
		session.ID,
	)
	return err
}

// Running Agent operations

// CreateRunningAgent creates a new running agent
func (s *UnifiedStore) CreateRunningAgent(agent RunningAgent) error {
	query := `INSERT INTO running_agents (agent_id, harness, session_id, pid, started_at, last_heartbeat, status, current_task, metadata_json)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		agent.AgentID, agent.Harness, nullString(agent.SessionID), agent.PID,
		agent.StartedAt.Format(time.RFC3339Nano), agent.LastHeartbeat.Format(time.RFC3339Nano),
		agent.Status, agent.CurrentTask, agent.MetadataJSON,
	)
	return err
}

// UpdateRunningAgent updates a running agent
func (s *UnifiedStore) UpdateRunningAgent(agent RunningAgent) error {
	query := `UPDATE running_agents SET
		harness = ?, session_id = ?, pid = ?, last_heartbeat = ?,
		status = ?, current_task = ?, metadata_json = ?
	WHERE agent_id = ?`

	_, err := s.db.Exec(query,
		agent.Harness, nullString(agent.SessionID), agent.PID,
		agent.LastHeartbeat.Format(time.RFC3339Nano),
		agent.Status, agent.CurrentTask, agent.MetadataJSON,
		agent.AgentID,
	)
	return err
}

// GetRunningAgent retrieves a running agent by ID
func (s *UnifiedStore) GetRunningAgent(id string) (*RunningAgent, error) {
	query := `SELECT agent_id, harness, session_id, pid, started_at, last_heartbeat, status, current_task, metadata_json
	FROM running_agents WHERE agent_id = ?`

	row := s.db.QueryRow(query, id)
	return scanRunningAgent(row)
}

// ListRunningAgents lists all running agents
func (s *UnifiedStore) ListRunningAgents(harness string) ([]RunningAgent, error) {
	query := `SELECT agent_id, harness, session_id, pid, started_at, last_heartbeat, status, current_task, metadata_json
	FROM running_agents`
	
	if harness != "" {
		query += " WHERE harness = ?"
		query += " ORDER BY last_heartbeat DESC"
		rows, err := s.db.Query(query, harness)
		if err != nil {
			return nil, err
		}
		defer rows.Close()
		return scanRunningAgents(rows)
	}
	
	query += " ORDER BY last_heartbeat DESC"
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return scanRunningAgents(rows)
}

// DeleteRunningAgent removes a running agent
func (s *UnifiedStore) DeleteRunningAgent(id string) error {
	_, err := s.db.Exec("DELETE FROM running_agents WHERE agent_id = ?", id)
	return err
}

// Task operations

// CreateTask creates a new task
func (s *UnifiedStore) CreateTask(task Task) error {
	query := `INSERT INTO tasks (task_id, session_id, team_id, title, description, priority, state, assigned_agent, created_at, updated_at, started_at, completed_at, result_json, error_message)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		task.TaskID, nullString(task.SessionID), nullString(task.TeamID),
		task.Title, task.Description, task.Priority, task.State,
		nullString(task.AssignedAgent),
		task.CreatedAt.Format(time.RFC3339Nano), task.UpdatedAt.Format(time.RFC3339Nano),
		nullTime(task.StartedAt), nullTime(task.CompletedAt),
		task.ResultJSON, task.ErrorMessage,
	)
	return err
}

// UpdateTask updates a task
func (s *UnifiedStore) UpdateTask(task Task) error {
	query := `UPDATE tasks SET
		session_id = ?, team_id = ?, title = ?, description = ?,
		priority = ?, state = ?, assigned_agent = ?,
		updated_at = ?, started_at = ?, completed_at = ?,
		result_json = ?, error_message = ?
	WHERE task_id = ?`

	_, err := s.db.Exec(query,
		nullString(task.SessionID), nullString(task.TeamID),
		task.Title, task.Description,
		task.Priority, task.State, nullString(task.AssignedAgent),
		task.UpdatedAt.Format(time.RFC3339Nano),
		nullTime(task.StartedAt), nullTime(task.CompletedAt),
		task.ResultJSON, task.ErrorMessage,
		task.TaskID,
	)
	return err
}

// ListTasks lists tasks with optional filters
func (s *UnifiedStore) ListTasks(state string, assignedAgent string) ([]Task, error) {
	query := `SELECT task_id, session_id, team_id, title, description, priority, state, assigned_agent, created_at, updated_at, started_at, completed_at, result_json, error_message
	FROM tasks WHERE 1=1`
	
	args := []interface{}{}
	
	if state != "" {
		query += " AND state = ?"
		args = append(args, state)
	}
	if assignedAgent != "" {
		query += " AND assigned_agent = ?"
		args = append(args, assignedAgent)
	}
	
	query += " ORDER BY priority ASC, created_at DESC"

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []Task
	for rows.Next() {
		t, err := scanTaskRows(rows)
		if err != nil {
			return nil, err
		}
		tasks = append(tasks, *t)
	}
	return tasks, nil
}

// GetPendingTasks returns all pending tasks
func (s *UnifiedStore) GetPendingTasks() ([]Task, error) {
	return s.ListTasks("pending", "")
}

// Message operations

// CreateMessage creates a new agent message
func (s *UnifiedStore) CreateMessage(msg AgentMessage) error {
	query := `INSERT INTO agent_messages (message_id, from_agent, to_agent, session_id, message_type, payload_json, priority, sent_at, received_at, acknowledged, delivery_status)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		msg.MessageID, msg.FromAgent, msg.ToAgent, nullString(msg.SessionID),
		msg.MessageType, msg.PayloadJSON, msg.Priority,
		msg.SentAt.Format(time.RFC3339Nano), nullTime(msg.ReceivedAt),
		msg.Acknowledged, msg.DeliveryStatus,
	)
	return err
}

// GetMessagesForAgent retrieves all messages for an agent
func (s *UnifiedStore) GetMessagesForAgent(agentID string) ([]AgentMessage, error) {
	query := `SELECT message_id, from_agent, to_agent, session_id, message_type, payload_json, priority, sent_at, received_at, acknowledged, delivery_status
	FROM agent_messages WHERE to_agent = ? ORDER BY sent_at DESC LIMIT 100`

	rows, err := s.db.Query(query, agentID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []AgentMessage
	for rows.Next() {
		m, err := scanMessageRows(rows)
		if err != nil {
			return nil, err
		}
		messages = append(messages, *m)
	}
	return messages, nil
}

// AcknowledgeMessage marks a message as acknowledged
func (s *UnifiedStore) AcknowledgeMessage(messageID string) error {
	query := `UPDATE agent_messages SET acknowledged = TRUE, received_at = ? WHERE message_id = ?`
	_, err := s.db.Exec(query, time.Now().Format(time.RFC3339Nano), messageID)
	return err
}

// Audit operations

// CreateAuditEntry creates an audit log entry
func (s *UnifiedStore) CreateAuditEntry(entry AuditLogEntry) error {
	query := `INSERT INTO audit_log (audit_id, timestamp, agent_id, session_id, event_type, details_json)
	VALUES (?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		entry.AuditID, entry.Timestamp.Format(time.RFC3339Nano),
		nullString(entry.AgentID), nullString(entry.SessionID),
		entry.EventType, entry.DetailsJSON,
	)
	return err
}

// GetAuditLog retrieves audit entries with optional filters
func (s *UnifiedStore) GetAuditLog(agentID string, sessionID string, eventType string, limit int) ([]AuditLogEntry, error) {
	query := `SELECT audit_id, timestamp, agent_id, session_id, event_type, details_json
	FROM audit_log WHERE 1=1`
	
	args := []interface{}{}
	
	if agentID != "" {
		query += " AND agent_id = ?"
		args = append(args, agentID)
	}
	if sessionID != "" {
		query += " AND session_id = ?"
		args = append(args, sessionID)
	}
	if eventType != "" {
		query += " AND event_type = ?"
		args = append(args, eventType)
	}
	
	query += " ORDER BY timestamp DESC"
	
	if limit > 0 {
		query += fmt.Sprintf(" LIMIT %d", limit)
	} else {
		query += " LIMIT 100"
	}

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var entries []AuditLogEntry
	for rows.Next() {
		e, err := scanAuditRows(rows)
		if err != nil {
			return nil, err
		}
		entries = append(entries, *e)
	}
	return entries, nil
}

// Harness sync operations

// UpdateHarnessSync updates the sync status for a harness
func (s *UnifiedStore) UpdateHarnessSync(sync HarnessSync) error {
	query := `INSERT INTO harness_sync (harness, last_sync_at, last_session_at, session_count, status, error_message, metadata_json)
	VALUES (?, ?, ?, ?, ?, ?, ?)
	ON CONFLICT(harness) DO UPDATE SET
		last_sync_at = excluded.last_sync_at,
		last_session_at = excluded.last_session_at,
		session_count = excluded.session_count,
		status = excluded.status,
		error_message = excluded.error_message,
		metadata_json = excluded.metadata_json`

	_, err := s.db.Exec(query,
		sync.Harness, sync.LastSyncAt.Format(time.RFC3339Nano),
		nullTime(sync.LastSessionAt), sync.SessionCount,
		sync.Status, sync.ErrorMessage, sync.MetadataJSON,
	)
	return err
}

// GetHarnessSync retrieves sync status for all harnesses
func (s *UnifiedStore) GetHarnessSync() ([]HarnessSync, error) {
	query := `SELECT harness, last_sync_at, last_session_at, session_count, status, error_message, metadata_json FROM harness_sync ORDER BY last_sync_at DESC`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var syncs []HarnessSync
	for rows.Next() {
		var sync HarnessSync
		var lastSyncAt, lastSessionAt, metadataJSON sql.NullString
		var sessionCount sql.NullInt64
		var errorMessage sql.NullString
		
		err := rows.Scan(&sync.Harness, &lastSyncAt, &lastSessionAt, &sessionCount, &sync.Status, &errorMessage, &metadataJSON)
		if err != nil {
			return nil, err
		}
		
		if lastSyncAt.Valid {
			sync.LastSyncAt, _ = time.Parse(time.RFC3339Nano, lastSyncAt.String)
		}
		if lastSessionAt.Valid {
			sync.LastSessionAt, _ = time.Parse(time.RFC3339Nano, lastSessionAt.String)
		}
		if sessionCount.Valid {
			sync.SessionCount = int(sessionCount.Int64)
		}
		if errorMessage.Valid {
			sync.ErrorMessage = errorMessage.String
		}
		if metadataJSON.Valid {
			sync.MetadataJSON = metadataJSON.String
		}
		
		syncs = append(syncs, sync)
	}
	return syncs, nil
}

// DeleteSession removes a session
func (s *UnifiedStore) DeleteSession(id string) error {
	_, err := s.db.Exec("DELETE FROM sessions WHERE session_id = ?", id)
	return err
}

// RecordHarnessSync records sync status for a harness
func (s *UnifiedStore) RecordHarnessSync(sync HarnessSync) error {
	return s.UpdateHarnessSync(sync)
}

// GetHarnessSyncStatus retrieves sync status for a specific harness
func (s *UnifiedStore) GetHarnessSyncStatus(harness string) ([]HarnessSync, error) {
	if harness == "" {
		return s.GetHarnessSync()
	}

	query := `SELECT harness, last_sync_at, last_session_at, session_count, status, error_message, metadata_json
		FROM harness_sync WHERE harness = ? ORDER BY last_sync_at DESC LIMIT 1`

	rows, err := s.db.Query(query, harness)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var syncs []HarnessSync
	for rows.Next() {
		var sync HarnessSync
		var lastSyncAt, lastSessionAt, metadataJSON sql.NullString
		var sessionCount sql.NullInt64
		var errorMessage sql.NullString

		err := rows.Scan(&sync.Harness, &lastSyncAt, &lastSessionAt, &sessionCount, &sync.Status, &errorMessage, &metadataJSON)
		if err != nil {
			return nil, err
		}

		if lastSyncAt.Valid {
			sync.LastSyncAt, _ = time.Parse(time.RFC3339Nano, lastSyncAt.String)
		}
		if lastSessionAt.Valid {
			sync.LastSessionAt, _ = time.Parse(time.RFC3339Nano, lastSessionAt.String)
		}
		if sessionCount.Valid {
			sync.SessionCount = int(sessionCount.Int64)
		}
		if errorMessage.Valid {
			sync.ErrorMessage = errorMessage.String
		}
		if metadataJSON.Valid {
			sync.MetadataJSON = metadataJSON.String
		}

		syncs = append(syncs, sync)
	}
	return syncs, nil
}

// UpsertSession creates or updates a session
func (s *UnifiedStore) UpsertSession(session Session) error {
	// Try to update first
	existing, err := s.GetSession(session.ID)
	if err == nil && existing != nil {
		// Update existing
		session.PromptTokens = existing.PromptTokens
		session.CompletionTokens = existing.CompletionTokens
		session.CostUSD = existing.CostUSD
		session.MessagesJSON = existing.MessagesJSON
		session.GoalsJSON = existing.GoalsJSON
		session.ArtifactsJSON = existing.ArtifactsJSON
		session.TeamID = existing.TeamID
		session.ParentSessionID = existing.ParentSessionID
		session.DelegationChainJSON = existing.DelegationChainJSON
		session.ResolutionNotes = existing.ResolutionNotes
		session.MetadataJSON = existing.MetadataJSON
		session.IndexedAt = existing.IndexedAt
		return s.UpdateSession(session)
	}

	// Create new
	if session.IndexedAt.IsZero() {
		session.IndexedAt = time.Now()
	}
	return s.CreateSession(session)
}

// GetRunningAgents returns all running agents
func (s *UnifiedStore) GetRunningAgents() ([]RunningAgent, error) {
	return s.ListRunningAgents("")
}

// SessionFilter represents filters for listing sessions
type SessionFilter struct {
	Harness     string
	State       string
	TeamID      string
	WorkingDir  string
	All         bool
	SortBy      string
	Limit       int
}

// Helper functions

func nullString(s string) interface{} {
	if s == "" {
		return nil
	}
	return s
}

func nullTime(t time.Time) interface{} {
	if t.IsZero() {
		return nil
	}
	return t.Format(time.RFC3339Nano)
}

func parseTime(s string) time.Time {
	if s == "" || s == "{}" {
		return time.Time{}
	}
	t, err := time.Parse(time.RFC3339Nano, s)
	if err != nil {
		return time.Time{}
	}
	return t
}

func scanSession(row *sql.Row) (*Session, error) {
	var s Session
	var startedAt, endedAt, lastActivity, indexedAt sql.NullString
	var messagesJSON, summary, goalsJSON, artifactsJSON, delegationChain, resolutionNotes, metadataJSON sql.NullString
	var parentSessionID, teamID sql.NullString
	var state sql.NullString
	var completionState sql.NullString

	err := row.Scan(
		&s.ID, &s.Harness, &s.Provider, &s.Model, &s.ProjectPath, &s.WorkingDir,
		&state, &startedAt, &endedAt, &lastActivity,
		&s.PromptTokens, &s.CompletionTokens, &s.CostUSD,
		&messagesJSON, &summary, &goalsJSON, &artifactsJSON,
		&teamID, &parentSessionID, &delegationChain,
		&completionState, &resolutionNotes, &metadataJSON, &indexedAt,
	)
	if err != nil {
		return nil, err
	}

	if state.Valid { s.State = state.String }
	if completionState.Valid { s.CompletionState = completionState.String }
	if startedAt.Valid { s.StartedAt = parseTime(startedAt.String) }
	if endedAt.Valid { s.EndedAt = parseTime(endedAt.String) }
	if lastActivity.Valid { s.LastActivityAt = parseTime(lastActivity.String) }
	if indexedAt.Valid { s.IndexedAt = parseTime(indexedAt.String) }

	if messagesJSON.Valid { s.MessagesJSON = messagesJSON.String }
	if summary.Valid { s.Summary = summary.String }
	if goalsJSON.Valid { s.GoalsJSON = goalsJSON.String }
	if artifactsJSON.Valid { s.ArtifactsJSON = artifactsJSON.String }
	if delegationChain.Valid { s.DelegationChainJSON = delegationChain.String }
	if resolutionNotes.Valid { s.ResolutionNotes = resolutionNotes.String }
	if metadataJSON.Valid { s.MetadataJSON = metadataJSON.String }
	if teamID.Valid { s.TeamID = teamID.String }
	if parentSessionID.Valid { s.ParentSessionID = parentSessionID.String }

	return &s, nil
}

func scanSessionRows(rows *sql.Rows) (*Session, error) {
	var s Session
	var startedAt, endedAt, lastActivity, indexedAt sql.NullString
	var messagesJSON, summary, goalsJSON, artifactsJSON, delegationChain, resolutionNotes, metadataJSON sql.NullString
	var parentSessionID, teamID sql.NullString
	var state sql.NullString
	var completionState sql.NullString

	err := rows.Scan(
		&s.ID, &s.Harness, &s.Provider, &s.Model, &s.ProjectPath, &s.WorkingDir,
		&state, &startedAt, &endedAt, &lastActivity,
		&s.PromptTokens, &s.CompletionTokens, &s.CostUSD,
		&messagesJSON, &summary, &goalsJSON, &artifactsJSON,
		&teamID, &parentSessionID, &delegationChain,
		&completionState, &resolutionNotes, &metadataJSON, &indexedAt,
	)
	if err != nil {
		return nil, err
	}

	if state.Valid { s.State = state.String }
	if completionState.Valid { s.CompletionState = completionState.String }
	if startedAt.Valid { s.StartedAt = parseTime(startedAt.String) }
	if endedAt.Valid { s.EndedAt = parseTime(endedAt.String) }
	if lastActivity.Valid { s.LastActivityAt = parseTime(lastActivity.String) }
	if indexedAt.Valid { s.IndexedAt = parseTime(indexedAt.String) }

	if messagesJSON.Valid { s.MessagesJSON = messagesJSON.String }
	if summary.Valid { s.Summary = summary.String }
	if goalsJSON.Valid { s.GoalsJSON = goalsJSON.String }
	if artifactsJSON.Valid { s.ArtifactsJSON = artifactsJSON.String }
	if delegationChain.Valid { s.DelegationChainJSON = delegationChain.String }
	if resolutionNotes.Valid { s.ResolutionNotes = resolutionNotes.String }
	if metadataJSON.Valid { s.MetadataJSON = metadataJSON.String }
	if teamID.Valid { s.TeamID = teamID.String }
	if parentSessionID.Valid { s.ParentSessionID = parentSessionID.String }

	return &s, nil
}

func scanRunningAgent(row *sql.Row) (*RunningAgent, error) {
	var a RunningAgent
	var startedAt, lastHeartbeat, metadataJSON sql.NullString
	var sessionID sql.NullString
	var pid sql.NullInt64

	err := row.Scan(&a.AgentID, &a.Harness, &sessionID, &pid, &startedAt, &lastHeartbeat, &a.Status, &a.CurrentTask, &metadataJSON)
	if err != nil {
		return nil, err
	}

	if startedAt.Valid { a.StartedAt = parseTime(startedAt.String) }
	if lastHeartbeat.Valid { a.LastHeartbeat = parseTime(lastHeartbeat.String) }
	if sessionID.Valid { a.SessionID = sessionID.String }
	if pid.Valid { a.PID = int(pid.Int64) }
	if metadataJSON.Valid { a.MetadataJSON = metadataJSON.String }

	return &a, nil
}

func scanRunningAgents(rows *sql.Rows) ([]RunningAgent, error) {
	var agents []RunningAgent
	for rows.Next() {
		var a RunningAgent
		var startedAt, lastHeartbeat, metadataJSON sql.NullString
		var sessionID sql.NullString
		var pid sql.NullInt64

		err := rows.Scan(&a.AgentID, &a.Harness, &sessionID, &pid, &startedAt, &lastHeartbeat, &a.Status, &a.CurrentTask, &metadataJSON)
		if err != nil {
			return nil, err
		}

		if startedAt.Valid { a.StartedAt = parseTime(startedAt.String) }
		if lastHeartbeat.Valid { a.LastHeartbeat = parseTime(lastHeartbeat.String) }
		if sessionID.Valid { a.SessionID = sessionID.String }
		if pid.Valid { a.PID = int(pid.Int64) }
		if metadataJSON.Valid { a.MetadataJSON = metadataJSON.String }

		agents = append(agents, a)
	}
	return agents, nil
}

func scanTaskRows(rows *sql.Rows) (*Task, error) {
	var t Task
	var createdAt, updatedAt, startedAt, completedAt sql.NullString
	var sessionID, teamID, assignedAgent, resultJSON, errorMessage sql.NullString

	err := rows.Scan(&t.TaskID, &sessionID, &teamID, &t.Title, &t.Description, &t.Priority, &t.State, &assignedAgent, &createdAt, &updatedAt, &startedAt, &completedAt, &resultJSON, &errorMessage)
	if err != nil {
		return nil, err
	}

	t.CreatedAt = parseTime(createdAt.String)
	t.UpdatedAt = parseTime(updatedAt.String)
	t.StartedAt = parseTime(startedAt.String)
	t.CompletedAt = parseTime(completedAt.String)
	if sessionID.Valid { t.SessionID = sessionID.String }
	if teamID.Valid { t.TeamID = teamID.String }
	if assignedAgent.Valid { t.AssignedAgent = assignedAgent.String }
	if resultJSON.Valid { t.ResultJSON = resultJSON.String }
	if errorMessage.Valid { t.ErrorMessage = errorMessage.String }

	return &t, nil
}

func scanMessageRows(rows *sql.Rows) (*AgentMessage, error) {
	var m AgentMessage
	var sentAt, receivedAt sql.NullString
	var sessionID, payloadJSON sql.NullString

	err := rows.Scan(&m.MessageID, &m.FromAgent, &m.ToAgent, &sessionID, &m.MessageType, &payloadJSON, &m.Priority, &sentAt, &receivedAt, &m.Acknowledged, &m.DeliveryStatus)
	if err != nil {
		return nil, err
	}

	m.SentAt = parseTime(sentAt.String)
	m.ReceivedAt = parseTime(receivedAt.String)
	if sessionID.Valid { m.SessionID = sessionID.String }
	if payloadJSON.Valid { m.PayloadJSON = payloadJSON.String }

	return &m, nil
}

func scanAuditRows(rows *sql.Rows) (*AuditLogEntry, error) {
	var e AuditLogEntry
	var timestamp, detailsJSON sql.NullString
	var agentID, sessionID sql.NullString

	err := rows.Scan(&e.AuditID, &timestamp, &agentID, &sessionID, &e.EventType, &detailsJSON)
	if err != nil {
		return nil, err
	}

	e.Timestamp = parseTime(timestamp.String)
	if agentID.Valid { e.AgentID = agentID.String }
	if sessionID.Valid { e.SessionID = sessionID.String }
	if detailsJSON.Valid { e.DetailsJSON = detailsJSON.String }

	return &e, nil
}
