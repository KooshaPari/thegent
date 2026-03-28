package adapter

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

// HarnessType represents the type of harness
type HarnessType string

const (
	HarnessForge        HarnessType = "forge"
	HarnessCodex        HarnessType = "codex"
	HarnessCursor       HarnessType = "cursor"
	HarnessClaude       HarnessType = "claude"
	HarnessFactoryDroid HarnessType = "factory-droid"
)

// StartParams contains parameters for starting a new session
type StartParams struct {
	Provider string
	Model    string
	Dir      string
	Name     string
	Meta     map[string]interface{}
}

// SessionFilter represents filters for listing sessions
type SessionFilter struct {
	Harness    string
	All        bool
	SortBy     string
	Limit      int
	Offset     int
	State      string
	TeamID     string
	WorkingDir string
}

// SessionInfo contains session information from a harness
type SessionInfo struct {
	ID              string                 `json:"id"`
	Name            string                 `json:"name"`
	Provider        string                 `json:"provider"`
	Model           string                 `json:"model"`
	State           string                 `json:"state"`
	CreatedAt       time.Time              `json:"created_at"`
	UpdatedAt       time.Time              `json:"updated_at"`
	LastActivityAt  time.Time              `json:"last_activity_at"`
	LastMessage     string                 `json:"last_message"`
	MessagesCount   int                    `json:"messages_count"`
	PromptTokens    int                    `json:"prompt_tokens"`
	CompletionTokens int                    `json:"completion_tokens"`
	CostUSD         float64                `json:"cost_usd"`
	ProjectPath     string                 `json:"project_path"`
	WorkingDir      string                 `json:"working_directory"`
	Summary         string                 `json:"summary"`
	Metadata        map[string]interface{} `json:"metadata"`
}

// AgentInfo contains running agent information
type AgentInfo struct {
	ID           string                 `json:"id"`
	Harness      HarnessType            `json:"harness"`
	PID          int                    `json:"pid"`
	SessionID    string                 `json:"session_id"`
	StartedAt    time.Time              `json:"started_at"`
	Status       string                 `json:"status"`
	CurrentTask  string                 `json:"current_task"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// MessageSnapshot represents a message in a session (for transfer/snapshot)
type MessageSnapshot struct {
	Role      string    `json:"role"`
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
}

// HarnessAdapter defines the interface for harness interactions
type HarnessAdapter interface {
	// Type returns the harness type
	Type() HarnessType

	// GetPriority returns the adapter priority (1=highest)
	GetPriority() int

	// ListSessions returns all sessions from this harness
	ListSessions() ([]SessionInfo, error)

	// ListSessionsFiltered returns sessions with optional filters
	ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error)

	// GetSession returns a specific session
	GetSession(id string) (*SessionInfo, error)

	// ListAgents returns all running agents from this harness
	ListAgents() ([]AgentInfo, error)

	// StartSession starts a new session
	StartSession(params StartParams) (*SessionInfo, error)

	// OpenSession opens an existing session
	OpenSession(id string, target string) error

	// TransferSession transfers a session to this harness
	TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error)

	// SendMessage sends a message to an agent
	SendMessage(toAgent string, message string) error

	// IsAvailable checks if the harness is available
	IsAvailable() bool

	// GetSessionMessages returns messages from a session (for snapshot/transfer)
	GetSessionMessages(sessionID string) ([]MessageSnapshot, error)
}

// NewAdapter creates an adapter for the specified harness type
func NewAdapter(harness HarnessType) HarnessAdapter {
	switch harness {
	case HarnessForge:
		return &ForgeAdapter{}
	case HarnessCodex:
		return &CodexAdapter{}
	case HarnessCursor:
		return &CursorAdapter{}
	case HarnessClaude:
		return &ClaudeAdapter{}
	case HarnessFactoryDroid:
		return &DroidAdapter{}
	default:
		return &GenericAdapter{harness: harness}
	}
}

// GenericAdapter provides a base implementation
type GenericAdapter struct {
	harness HarnessType
}

func (a *GenericAdapter) Type() HarnessType { return a.harness }
func (a *GenericAdapter) GetPriority() int { return 10 } // Low priority
func (a *GenericAdapter) IsAvailable() bool {
	cmd := exec.Command("which", string(a.harness))
	return cmd.Run() == nil
}
func (a *GenericAdapter) GetSession(id string) (*SessionInfo, error) {
	return nil, fmt.Errorf("not implemented")
}
func (a *GenericAdapter) ListSessions() ([]SessionInfo, error) {
	return []SessionInfo{}, nil
}
func (a *GenericAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	return []SessionInfo{}, nil
}
func (a *GenericAdapter) ListAgents() ([]AgentInfo, error) {
	return []AgentInfo{}, nil
}
func (a *GenericAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	return nil, fmt.Errorf("not implemented")
}
func (a *GenericAdapter) OpenSession(id string, target string) error {
	return fmt.Errorf("not implemented")
}
func (a *GenericAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	return nil, fmt.Errorf("not implemented")
}
func (a *GenericAdapter) SendMessage(toAgent string, message string) error {
	return fmt.Errorf("not implemented")
}
func (a *GenericAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	return []MessageSnapshot{}, nil
}

// ForgeAdapter implements HarnessAdapter for Forge
type ForgeAdapter struct {
	GenericAdapter
	apiURL string
	client *ForgeClient
}

func NewForgeAdapterV2() *ForgeAdapter {
	client := NewForgeClient()
	return &ForgeAdapter{
		GenericAdapter: GenericAdapter{harness: HarnessForge},
		apiURL:         client.BaseURL,
		client:         client,
	}
}

func (a *ForgeAdapter) Type() HarnessType { return HarnessForge }

func (a *ForgeAdapter) GetPriority() int { return 1 }

func (a *ForgeAdapter) IsAvailable() bool {
	// Check if forge is running
	cmd := exec.Command("pgrep", "-f", "forge")
	return cmd.Run() == nil
}

func (a *ForgeAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	// Forge API integration would fetch messages here
	// For now, return empty - requires Forge API
	return []MessageSnapshot{}, nil
}

func (a *ForgeAdapter) ListSessions() ([]SessionInfo, error) {
	// Use real Forge API if configured
	if a.client != nil && a.client.IsConfigured() {
		sessions, err := a.client.ListSessions()
		if err == nil {
			var result []SessionInfo
			for _, s := range sessions {
				result = append(result, SessionInfo{
					ID:             s.ID,
					Name:           s.Name,
					Model:          s.Model,
					State:          s.Status,
					CreatedAt:      time.Now(),
					LastActivityAt: time.Now(),
					Metadata:       s.Metadata,
				})
			}
			return result, nil
		}
		// Fall through to CLI/FS on error
	}
	
	// Try to use forge CLI if available
	cmd := exec.Command("forge", "session", "list", "--json")
	output, err := cmd.Output()
	if err != nil {
		// Fallback: parse from filesystem
		return a.listSessionsFromFS()
	}
	
	var sessions []SessionInfo
	if err := json.Unmarshal(output, &sessions); err != nil {
		return nil, err
	}
	return sessions, nil
}

func (a *ForgeAdapter) listSessionsFromFS() ([]SessionInfo, error) {
	home := os.Getenv("HOME")
	sessionsDir := home + "/.local/share/forge/sessions"
	
	entries, err := os.ReadDir(sessionsDir)
	if err != nil {
		return []SessionInfo{}, nil
	}
	
	var sessions []SessionInfo
	for _, entry := range entries {
		if entry.IsDir() {
			sessionFile := sessionsDir + "/" + entry.Name() + "/session.json"
			if data, err := os.ReadFile(sessionFile); err == nil {
				var session SessionInfo
				if json.Unmarshal(data, &session) == nil {
					sessions = append(sessions, session)
				}
			}
		}
	}
	return sessions, nil
}

func (a *ForgeAdapter) GetSession(id string) (*SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}
	for _, s := range sessions {
		if s.ID == id {
			return &s, nil
		}
	}
	return nil, fmt.Errorf("session not found: %s", id)
}

func (a *ForgeAdapter) ListAgents() ([]AgentInfo, error) {
	// Check running forge processes
	cmd := exec.Command("pgrep", "-a", "-f", "forge")
	output, err := cmd.Output()
	if err != nil {
		return []AgentInfo{}, nil
	}
	
	var agents []AgentInfo
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 2 {
			pid, _ := strconv.Atoi(parts[0])
			agents = append(agents, AgentInfo{
				ID:      fmt.Sprintf("forge-%d", pid),
				Harness: HarnessForge,
				PID:     pid,
				Status:  "running",
			})
		}
	}
	return agents, nil
}

func (a *ForgeAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	// Use real Forge API if configured
	if a.client != nil && a.client.IsConfigured() {
		req := ForgeCreateRequest{
			Model: params.Model,
			Name:  params.Name,
		}
		session, err := a.client.CreateSession(req)
		if err == nil {
			return &SessionInfo{
				ID:             session.ID,
				Name:           session.Name,
				Model:          session.Model,
				State:          session.Status,
				CreatedAt:      time.Now(),
				LastActivityAt: time.Now(),
				Metadata:       session.Metadata,
			}, nil
		}
		// Fall through to stub on error
	}
	
	sessionID := uuid.New().String()
	now := time.Now()
	
	return &SessionInfo{
		ID:             sessionID,
		Name:           params.Name,
		Model:          params.Model,
		State:          "active",
		CreatedAt:      now,
		LastActivityAt: now,
		MessagesCount:  0,
		WorkingDir:     params.Dir,
		Metadata:       params.Meta,
	}, nil
}

func (a *ForgeAdapter) OpenSession(id string, target string) error {
	// Open in default harness (forge)
	cmd := exec.Command("forge", "session", "open", id)
	return cmd.Run()
}

func (a *ForgeAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	// Get source session
	session, err := a.GetSession(id)
	if err != nil {
		return nil, err
	}
	
	// Create new session with transferred data
	newSession := &SessionInfo{
		ID:             uuid.New().String(),
		Name:           session.Name + " (transferred)",
		Model:          session.Model,
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
		WorkingDir:     session.WorkingDir,
		Metadata: map[string]interface{}{
			"source_session": id,
			"source_harness": fromHarness,
		},
	}
	
	return newSession, nil
}

func (a *ForgeAdapter) SendMessage(toAgent string, message string) error {
	// Send message via forge IPC
	cmd := exec.Command("forge", "agent", "send", toAgent, "--message", message)
	return cmd.Run()
}

func (a *ForgeAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}

	var result []SessionInfo
	for _, s := range sessions {
		if filter.Limit > 0 && len(result) >= filter.Limit {
			break
		}
		result = append(result, s)
	}

	return result, nil
}

// CodexAdapter implements HarnessAdapter for Codex
type CodexAdapter struct {
	GenericAdapter
	serverAddr string
}

func NewCodexAdapter() *CodexAdapter {
	addr := os.Getenv("CODEX_SERVER_ADDR")
	if addr == "" {
		addr = "localhost:8081"
	}
	return &CodexAdapter{
		GenericAdapter: GenericAdapter{harness: HarnessCodex},
		serverAddr:     addr,
	}
}

func (a *CodexAdapter) Type() HarnessType { return HarnessCodex }

func (a *CodexAdapter) GetPriority() int { return 2 }

func (a *CodexAdapter) IsAvailable() bool {
	// Check for codex process or server
	cmd := exec.Command("pgrep", "-f", "codex")
	return cmd.Run() == nil
}

func (a *CodexAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	// Codex app-server integration would fetch messages here
	return []MessageSnapshot{}, nil
}

func (a *CodexAdapter) ListSessions() ([]SessionInfo, error) {
	// Try codex CLI
	cmd := exec.Command("codex", "sessions", "list", "--json")
	output, err := cmd.Output()
	if err != nil {
		// Fallback: parse from codex data directory
		return a.listSessionsFromFS()
	}
	
	var sessions []SessionInfo
	if err := json.Unmarshal(output, &sessions); err != nil {
		return nil, err
	}
	return sessions, nil
}

func (a *CodexAdapter) listSessionsFromFS() ([]SessionInfo, error) {
	home := os.Getenv("HOME")
	// Codex typically stores sessions in various locations
	locations := []string{
		home + "/.codex/sessions",
		home + "/Library/Application Support/Codex/sessions",
	}
	
	var allSessions []SessionInfo
	for _, loc := range locations {
		entries, err := os.ReadDir(loc)
		if err != nil {
			continue
		}
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".json") {
				if data, err := os.ReadFile(loc + "/" + entry.Name()); err == nil {
					var session SessionInfo
					if json.Unmarshal(data, &session) == nil {
						allSessions = append(allSessions, session)
					}
				}
			}
		}
	}
	return allSessions, nil
}

func (a *CodexAdapter) GetSession(id string) (*SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}
	for _, s := range sessions {
		if s.ID == id {
			return &s, nil
		}
	}
	return nil, fmt.Errorf("session not found: %s", id)
}

func (a *CodexAdapter) ListAgents() ([]AgentInfo, error) {
	// Check for codex agent processes
	cmd := exec.Command("pgrep", "-a", "-f", "codex-agent")
	output, err := cmd.Output()
	if err != nil {
		return []AgentInfo{}, nil
	}
	
	var agents []AgentInfo
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 2 {
			pid, _ := strconv.Atoi(parts[0])
			agents = append(agents, AgentInfo{
				ID:      fmt.Sprintf("codex-%d", pid),
				Harness: HarnessCodex,
				PID:     pid,
				Status:  "running",
			})
		}
	}
	return agents, nil
}

func (a *CodexAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	sessionID := uuid.New().String()
	now := time.Now()
	
	return &SessionInfo{
		ID:             sessionID,
		Name:           params.Name,
		Model:          params.Model,
		State:          "active",
		CreatedAt:      now,
		LastActivityAt: now,
		MessagesCount:  0,
		WorkingDir:     params.Dir,
		Metadata:       params.Meta,
	}, nil
}

func (a *CodexAdapter) OpenSession(id string, target string) error {
	cmd := exec.Command("codex", "session", "open", id)
	return cmd.Run()
}

func (a *CodexAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	session, err := a.GetSession(id)
	if err != nil {
		return nil, err
	}
	
	return &SessionInfo{
		ID:             uuid.New().String(),
		Name:           session.Name + " (transferred)",
		Model:          session.Model,
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
		WorkingDir:     session.WorkingDir,
		Metadata: map[string]interface{}{
			"source_session": id,
			"source_harness": fromHarness,
		},
	}, nil
}

func (a *CodexAdapter) SendMessage(toAgent string, message string) error {
	cmd := exec.Command("codex", "agent", "send", toAgent, "--message", message)
	return cmd.Run()
}

// CodexClient is an HTTP client for Codex API
type CodexClient struct {
	BaseURL string
	APIKey  string
}

func NewCodexClient() *CodexClient {
	baseURL := os.Getenv("CODEX_API_URL")
	if baseURL == "" {
		baseURL = "http://localhost:8081"
	}
	apiKey := os.Getenv("CODEX_API_KEY")

	return &CodexClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

// IsConfigured returns true if the client is properly configured
func (c *CodexClient) IsConfigured() bool {
	return c.APIKey != "" || os.Getenv("CODEX_API_KEY") != ""
}

// CodexSession represents a session from Codex API
type CodexSession struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Status    string    `json:"status"`
	Model     string    `json:"model"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// CodexSessionsResponse is the API response for list
type CodexSessionsResponse struct {
	Sessions []CodexSession `json:"sessions"`
}

// CodexCreateRequest is the request to create a session
type CodexCreateRequest struct {
	Name  string `json:"name"`
	Model string `json:"model"`
}

// CodexAPI calls Codex REST API
func (c *CodexClient) CodexAPI(method, path string, body []byte) ([]byte, int, error) {
	url := c.BaseURL + path
	var reqBody *bytes.Reader
	if body != nil {
		reqBody = bytes.NewReader(body)
	}

	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, resp.StatusCode, err
	}
	return respBody, resp.StatusCode, nil
}

func (c *CodexClient) ListSessions() ([]CodexSession, error) {
	if !c.IsConfigured() {
		return []CodexSession{}, nil
	}

	respBody, status, err := c.CodexAPI("GET", "/api/sessions", nil)
	if err != nil {
		return nil, err
	}
	if status != 200 {
		return nil, fmt.Errorf("Codex API returned status %d", status)
	}

	var result CodexSessionsResponse
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, err
	}
	return result.Sessions, nil
}

func (c *CodexClient) GetSession(id string) (*CodexSession, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Codex client not configured")
	}

	respBody, status, err := c.CodexAPI("GET", "/api/sessions/"+id, nil)
	if err != nil {
		return nil, err
	}
	if status != 200 {
		return nil, fmt.Errorf("Codex API returned status %d", status)
	}

	var session CodexSession
	if err := json.Unmarshal(respBody, &session); err != nil {
		return nil, err
	}
	return &session, nil
}

func (c *CodexClient) CreateSession(req CodexCreateRequest) (*CodexSession, error) {
	if !c.IsConfigured() {
		return nil, fmt.Errorf("Codex client not configured")
	}

	body, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	respBody, status, err := c.CodexAPI("POST", "/api/sessions", body)
	if err != nil {
		return nil, err
	}
	if status != 201 {
		return nil, fmt.Errorf("Codex API returned status %d", status)
	}

	var session CodexSession
	if err := json.Unmarshal(respBody, &session); err != nil {
		return nil, err
	}
	return &session, nil
}

func (a *CodexAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}

	var result []SessionInfo
	for _, s := range sessions {
		if filter.Limit > 0 && len(result) >= filter.Limit {
			break
		}
		result = append(result, s)
	}

	return result, nil
}

// CursorAdapter implements HarnessAdapter for Cursor
type CursorAdapter struct {
	GenericAdapter
}

func NewCursorAdapter() *CursorAdapter {
	return &CursorAdapter{GenericAdapter{harness: HarnessCursor}}
}

func (a *CursorAdapter) Type() HarnessType { return HarnessCursor }

func (a *CursorAdapter) GetPriority() int { return 3 }

func (a *CursorAdapter) IsAvailable() bool {
	// Check for Cursor process
	cmd := exec.Command("pgrep", "-f", "cursor")
	return cmd.Run() == nil
}

func (a *CursorAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	// Cursor session files integration would fetch messages here
	return []MessageSnapshot{}, nil
}

func (a *CursorAdapter) ListSessions() ([]SessionInfo, error) {
	// Cursor stores sessions in its app data
	home := os.Getenv("HOME")
	locations := []string{
		home + "/.cursor/data/sessions",
		home + "/Library/Application Support/Cursor/sessions",
	}
	
	var sessions []SessionInfo
	for _, loc := range locations {
		entries, err := os.ReadDir(loc)
		if err != nil {
			continue
		}
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".json") {
				if data, err := os.ReadFile(loc + "/" + entry.Name()); err == nil {
					var session SessionInfo
					if json.Unmarshal(data, &session) == nil {
						sessions = append(sessions, session)
					}
				}
			}
		}
	}
	return sessions, nil
}

func (a *CursorAdapter) GetSession(id string) (*SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}
	for _, s := range sessions {
		if s.ID == id {
			return &s, nil
		}
	}
	return nil, fmt.Errorf("session not found: %s", id)
}

func (a *CursorAdapter) ListAgents() ([]AgentInfo, error) {
	cmd := exec.Command("pgrep", "-a", "-f", "cursor")
	output, err := cmd.Output()
	if err != nil {
		return []AgentInfo{}, nil
	}
	
	var agents []AgentInfo
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 2 {
			pid, _ := strconv.Atoi(parts[0])
			agents = append(agents, AgentInfo{
				ID:      fmt.Sprintf("cursor-%d", pid),
				Harness: HarnessCursor,
				PID:     pid,
				Status:  "running",
			})
		}
	}
	return agents, nil
}

func (a *CursorAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	// Use Cursor CLI if available
	cmd := exec.Command("cursor", "--new-session")
	if params.Dir != "" {
		cmd = exec.Command("cursor", "--new-session", "--directory", params.Dir)
	}
	if err := cmd.Run(); err != nil {
		// Fallback: create session record
	}
	
	return &SessionInfo{
		ID:             uuid.New().String(),
		Name:           params.Name,
		Model:          params.Model,
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
		WorkingDir:     params.Dir,
	}, nil
}

func (a *CursorAdapter) OpenSession(id string, target string) error {
	cmd := exec.Command("cursor", "--open-session", id)
	return cmd.Run()
}

func (a *CursorAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	return &SessionInfo{
		ID:             uuid.New().String(),
		Name:           "Transferred Session",
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
		Metadata: map[string]interface{}{
			"source_session": id,
			"source_harness": fromHarness,
		},
	}, nil
}

func (a *CursorAdapter) SendMessage(toAgent string, message string) error {
	// Cursor doesn't have a CLI for agent messaging
	return fmt.Errorf("Cursor does not support agent messaging via CLI")
}

func (a *CursorAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}

	var result []SessionInfo
	for _, s := range sessions {
		if filter.Limit > 0 && len(result) >= filter.Limit {
			break
		}
		result = append(result, s)
	}

	return result, nil
}

// ClaudeAdapter implements HarnessAdapter for Claude
type ClaudeAdapter struct {
	GenericAdapter
}

func NewClaudeAdapter() *ClaudeAdapter {
	return &ClaudeAdapter{GenericAdapter{harness: HarnessClaude}}
}

func (a *ClaudeAdapter) Type() HarnessType { return HarnessClaude }

func (a *ClaudeAdapter) GetPriority() int { return 4 }

func (a *ClaudeAdapter) IsAvailable() bool {
	cmd := exec.Command("which", "claude")
	return cmd.Run() == nil
}

func (a *ClaudeAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	// Claude CLI integration would fetch messages here
	return []MessageSnapshot{}, nil
}

func (a *ClaudeAdapter) ListSessions() ([]SessionInfo, error) {
	// Claude CLI stores conversations
	cmd := exec.Command("claude", "conversation", "list", "--json")
	output, err := cmd.Output()
	if err != nil {
		return []SessionInfo{}, nil
	}
	
	var sessions []SessionInfo
	if err := json.Unmarshal(output, &sessions); err != nil {
		return nil, err
	}
	return sessions, nil
}

func (a *ClaudeAdapter) GetSession(id string) (*SessionInfo, error) {
	cmd := exec.Command("claude", "conversation", "show", id, "--json")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("session not found: %s", id)
	}
	
	var session SessionInfo
	if err := json.Unmarshal(output, &session); err != nil {
		return nil, err
	}
	return &session, nil
}

func (a *ClaudeAdapter) ListAgents() ([]AgentInfo, error) {
	// Claude doesn't have persistent agents in the same way
	return []AgentInfo{}, nil
}

func (a *ClaudeAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	sessionID := uuid.New().String()
	
	cmd := exec.Command("claude", "conversation", "start")
	if params.Dir != "" {
		cmd = exec.Command("claude", "conversation", "start", "--project", params.Dir)
	}
	// Start in background
	cmd.Start()
	
	return &SessionInfo{
		ID:             sessionID,
		Name:           params.Name,
		Model:          params.Model,
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
		WorkingDir:     params.Dir,
	}, nil
}

func (a *ClaudeAdapter) OpenSession(id string, target string) error {
	cmd := exec.Command("claude", "conversation", "resume", id)
	return cmd.Run()
}

func (a *ClaudeAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	return &SessionInfo{
		ID:             uuid.New().String(),
		Name:           "Transferred from " + string(fromHarness),
		State:          "active",
		CreatedAt:      time.Now(),
		LastActivityAt: time.Now(),
	}, nil
}

func (a *ClaudeAdapter) SendMessage(toAgent string, message string) error {
	return fmt.Errorf("Claude does not support direct agent messaging")
}

func (a *ClaudeAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}

	var result []SessionInfo
	for _, s := range sessions {
		if filter.Limit > 0 && len(result) >= filter.Limit {
			break
		}
		result = append(result, s)
	}

	return result, nil
}

// DroidAdapter implements HarnessAdapter for Factory Droid
type DroidAdapter struct {
	GenericAdapter
	apiURL string
}

func NewDroidAdapter() *DroidAdapter {
	apiURL := os.Getenv("DROID_API_URL")
	if apiURL == "" {
		apiURL = "http://localhost:9090"
	}
	return &DroidAdapter{
		GenericAdapter: GenericAdapter{harness: HarnessFactoryDroid},
		apiURL:         apiURL,
	}
}

func (a *DroidAdapter) Type() HarnessType { return HarnessFactoryDroid }

func (a *DroidAdapter) GetPriority() int { return 5 }

func (a *DroidAdapter) IsAvailable() bool {
	cmd := exec.Command("pgrep", "-f", "factory-droid")
	return cmd.Run() == nil
}

func (a *DroidAdapter) GetSessionMessages(sessionID string) ([]MessageSnapshot, error) {
	// Factory-droid API integration would fetch messages here
	return []MessageSnapshot{}, nil
}

func (a *DroidAdapter) ListSessions() ([]SessionInfo, error) {
	// Query droid API
	cmd := exec.Command("droid", "session", "list", "--json")
	output, err := cmd.Output()
	if err != nil {
		return []SessionInfo{}, nil
	}
	
	var sessions []SessionInfo
	if err := json.Unmarshal(output, &sessions); err != nil {
		return nil, err
	}
	return sessions, nil
}

func (a *DroidAdapter) GetSession(id string) (*SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}
	for _, s := range sessions {
		if s.ID == id {
			return &s, nil
		}
	}
	return nil, fmt.Errorf("session not found: %s", id)
}

func (a *DroidAdapter) ListAgents() ([]AgentInfo, error) {
	cmd := exec.Command("droid", "agent", "list", "--json")
	output, err := cmd.Output()
	if err != nil {
		return []AgentInfo{}, nil
	}
	
	var agents []AgentInfo
	if err := json.Unmarshal(output, &agents); err != nil {
		return nil, err
	}
	return agents, nil
}

func (a *DroidAdapter) StartSession(params StartParams) (*SessionInfo, error) {
	cmd := exec.Command("droid", "session", "create", "--model", params.Model)
	if params.Name != "" {
		cmd = exec.Command("droid", "session", "create", "--model", params.Model, "--name", params.Name)
	}
	
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	
	var session SessionInfo
	if err := json.Unmarshal(output, &session); err != nil {
		return nil, err
	}
	return &session, nil
}

func (a *DroidAdapter) OpenSession(id string, target string) error {
	cmd := exec.Command("droid", "session", "attach", id)
	return cmd.Run()
}

func (a *DroidAdapter) TransferSession(id string, fromHarness HarnessType, params map[string]interface{}) (*SessionInfo, error) {
	cmd := exec.Command("droid", "session", "import", "--from", string(fromHarness), "--id", id)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	
	var session SessionInfo
	if err := json.Unmarshal(output, &session); err != nil {
		return nil, err
	}
	return &session, nil
}

func (a *DroidAdapter) SendMessage(toAgent string, message string) error {
	cmd := exec.Command("droid", "agent", "message", toAgent, "--message", message)
	return cmd.Run()
}

func (a *DroidAdapter) ListSessionsFiltered(filter SessionFilter) ([]SessionInfo, error) {
	sessions, err := a.ListSessions()
	if err != nil {
		return nil, err
	}

	var result []SessionInfo
	for _, s := range sessions {
		if filter.Limit > 0 && len(result) >= filter.Limit {
			break
		}
		result = append(result, s)
	}

	return result, nil
}

// AdapterRegistry manages all harness adapters
type AdapterRegistry struct {
	adapters map[HarnessType]HarnessAdapter
}

func NewAdapterRegistry() *AdapterRegistry {
	registry := &AdapterRegistry{
		adapters: make(map[HarnessType]HarnessAdapter),
	}
	
	// Register all adapters
	registry.adapters[HarnessForge] = NewForgeAdapterV2()
	registry.adapters[HarnessCodex] = NewCodexAdapter()
	registry.adapters[HarnessCursor] = NewCursorAdapter()
	registry.adapters[HarnessClaude] = NewClaudeAdapter()
	registry.adapters[HarnessFactoryDroid] = NewDroidAdapter()
	
	return registry
}

func (r *AdapterRegistry) Get(harness HarnessType) HarnessAdapter {
	if adapter, ok := r.adapters[harness]; ok {
		return adapter
	}
	return &GenericAdapter{harness: harness}
}

func (r *AdapterRegistry) ListAvailable() []HarnessType {
	var available []HarnessType
	for harness, adapter := range r.adapters {
		if adapter.IsAvailable() {
			available = append(available, harness)
		}
	}
	return available
}

func (r *AdapterRegistry) DiscoverAllAgents() ([]AgentInfo, error) {
	var allAgents []AgentInfo
	for _, adapter := range r.adapters {
		if adapter.IsAvailable() {
			agents, err := adapter.ListAgents()
			if err == nil {
				allAgents = append(allAgents, agents...)
			}
		}
	}
	return allAgents, nil
}

func (r *AdapterRegistry) DiscoverAllSessions() ([]SessionInfo, error) {
	var allSessions []SessionInfo
	for _, adapter := range r.adapters {
		if adapter.IsAvailable() {
			sessions, err := adapter.ListSessions()
			if err == nil {
				allSessions = append(allSessions, sessions...)
			}
		}
	}
	return allSessions, nil
}

// Helper function to extract PID from process info
func extractPID(processInfo string) int {
	re := regexp.MustCompile(`^\s*(\d+)`)
	matches := re.FindStringSubmatch(processInfo)
	if len(matches) > 1 {
		pid, _ := strconv.Atoi(matches[1])
		return pid
	}
	return 0
}
