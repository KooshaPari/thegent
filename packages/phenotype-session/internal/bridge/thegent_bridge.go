// thegent bridge - integrates pheno-session with thegent's Python codebase
package bridge

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Bridge connects pheno-session to thegent
type Bridge struct {
	thegentPath string
	pythonPath  string
}

// NewBridge creates a new thegent bridge
func NewBridge() *Bridge {
	// Find thegent installation
	thegentPath := os.Getenv("THEGENT_PATH")
	if thegentPath == "" {
		// Try common locations
		home, _ := os.UserHomeDir()
		paths := []string{
			filepath.Join(home, "CodeProjects", "Phenotype", "repos", "worktrees", "thegent"),
			filepath.Join(home, "CodeProjects", "Phenotype", "repos", "tooling", "thegent"),
			filepath.Join(home, "go", "src", "github.com", "KooshaPari", "thegent"),
		}
		for _, p := range paths {
			if _, err := os.Stat(p); err == nil {
				thegentPath = p
				break
			}
		}
	}

	return &Bridge{
		thegentPath: thegentPath,
		pythonPath:  findPython(),
	}
}

// findPython finds Python executable
func findPython() string {
	// Try python3 first
	if path, err := exec.LookPath("python3"); err == nil {
		return path
	}
	// Fall back to python
	if path, err := exec.LookPath("python"); err == nil {
		return path
	}
	return "python3"
}

// BridgeConfig holds bridge configuration
type BridgeConfig struct {
	SessionSync    bool `json:"session_sync"`
	AgentMonitor   bool `json:"agent_monitor"`
	TaskDelegate   bool `json:"task_delegate"`
	AutoStart      bool `json:"auto_start"`
	UnifiedIndex   bool `json:"unified_index"`
}

// DefaultConfig returns the default bridge config
func DefaultConfig() BridgeConfig {
	return BridgeConfig{
		SessionSync:    true,
		AgentMonitor:   true,
		TaskDelegate:   true,
		AutoStart:      false,
		UnifiedIndex:   true,
	}
}

// RunThegentCommand runs a thegent command via Python CLI
func (b *Bridge) RunThegentCommand(args ...string) (string, error) {
	if b.thegentPath == "" {
		return "", fmt.Errorf("thegent not found")
	}

	cliPath := filepath.Join(b.thegentPath, "cli.py")
	if _, err := os.Stat(cliPath); os.IsNotExist(err) {
		cliPath = filepath.Join(b.thegentPath, "src", "thegent", "cli.py")
	}
	if _, err := os.Stat(cliPath); os.IsNotExist(err) {
		return "", fmt.Errorf("thegent CLI not found at %s", b.thegentPath)
	}

	cmd := exec.Command(b.pythonPath, append([]string{cliPath}, args...)...)
	cmd.Dir = b.thegentPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("thegent command failed: %w\n%s", err, output)
	}

	return string(output), nil
}

// ListThegentSessions lists sessions from thegent
func (b *Bridge) ListThegentSessions() ([]ThegentSession, error) {
	output, err := b.RunThegentCommand("session", "list", "--json")
	if err != nil {
		// thegent might not have this command, return empty
		return []ThegentSession{}, nil
	}

	var sessions []ThegentSession
	if err := json.Unmarshal([]byte(output), &sessions); err != nil {
		return []ThegentSession{}, nil
	}

	return sessions, nil
}

// ThegentSession represents a session from thegent
type ThegentSession struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Harness     string `json:"harness"`
	Provider    string `json:"provider"`
	Model       string `json:"model"`
	State       string `json:"state"`
	CreatedAt   string `json:"created_at"`
	UpdatedAt   string `json:"updated_at"`
	WorkingDir  string `json:"working_dir"`
}

// GetSitbackStatus gets the sitback status from thegent
func (b *Bridge) GetSitbackStatus() (SitbackStatus, error) {
	output, err := b.RunThegentCommand("sitback", "--status", "--json")
	if err != nil {
		return SitbackStatus{}, err
	}

	var status SitbackStatus
	if err := json.Unmarshal([]byte(output), &status); err != nil {
		return SitbackStatus{}, err
	}

	return status, nil
}

// SitbackStatus represents thegent's sitback status
type SitbackStatus struct {
	ActiveAgents   int      `json:"active_agents"`
	RunningTasks   int      `json:"running_tasks"`
	QueuedTasks    int      `json:"queued_tasks"`
	LastActivity   string   `json:"last_activity"`
	HealthStatus   string   `json:"health_status"`
	Errors         []string `json:"errors"`
}

// StartThegentSitback starts thegent's sitback in background
func (b *Bridge) StartThegentSitback(profile string) error {
	_, err := b.RunThegentCommand("sitback", "--profile", profile)
	return err
}

// StopThegentSitback stops thegent's sitback
func (b *Bridge) StopThegentSitback() error {
	_, err := b.RunThegentCommand("sitback", "--stop")
	return err
}

// DelegateTaskToThegent delegates a task to thegent
func (b *Bridge) DelegateTaskToThegent(task string, harness string) (string, error) {
	output, err := b.RunThegentCommand("delegate", "--task", task, "--to", harness)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(output), nil
}

// SyncWithThegent syncs session data with thegent's unified index
func (b *Bridge) SyncWithThegent() error {
	_, err := b.RunThegentCommand("sync", "--source", "pheno-session")
	return err
}

// GetThegentAgents gets running agents from thegent
func (b *Bridge) GetThegentAgents() ([]ThegentAgent, error) {
	output, err := b.RunThegentCommand("agent", "list", "--json")
	if err != nil {
		return []ThegentAgent{}, nil
	}

	var agents []ThegentAgent
	if err := json.Unmarshal([]byte(output), &agents); err != nil {
		return []ThegentAgent{}, nil
	}

	return agents, nil
}

// ThegentAgent represents an agent from thegent
type ThegentAgent struct {
	ID          string `json:"id"`
	Type        string `json:"type"`
	Harness     string `json:"harness"`
	PID         int    `json:"pid"`
	Status      string `json:"status"`
	StartedAt   string `json:"started_at"`
	LastHeartbeat string `json:"last_heartbeat"`
}

// ConvertToPhenoSession converts a thegent session to pheno-session format
func (b *Bridge) ConvertToPhenoSession(tgSession ThegentSession) map[string]any {
	return map[string]any{
		"id":           tgSession.ID,
		"name":         tgSession.Name,
		"harness":      tgSession.Harness,
		"provider":      tgSession.Provider,
		"model":        tgSession.Model,
		"state":        tgSession.State,
		"source":       "thegent",
		"created_at":   tgSession.CreatedAt,
		"updated_at":   tgSession.UpdatedAt,
		"working_dir":  tgSession.WorkingDir,
	}
}

// InstallThegentHooks installs hooks for thegent integration
func (b *Bridge) InstallThegentHooks() error {
	// Create wrapper scripts for thegent integration
	home, _ := os.UserHomeDir()
	hooksDir := filepath.Join(home, ".local", "share", "phenotype", "hooks")
	os.MkdirAll(hooksDir, 0755)

	// Create sync hook
	syncHook := `#!/bin/bash
# Auto-sync sessions from thegent to pheno-session
pheno-session bridge --sync-thegent
`
	hookPath := filepath.Join(hooksDir, "post-session-create")
	os.WriteFile(hookPath, []byte(syncHook), 0755)

	return nil
}

// CheckHealth checks if thegent is healthy
func (b *Bridge) CheckHealth() error {
	_, err := b.RunThegentCommand("health")
	return err
}

// GetVersion gets thegent version
func (b *Bridge) GetVersion() string {
	output, err := b.RunThegentCommand("--version")
	if err != nil {
		return "unknown"
	}
	return strings.TrimSpace(output)
}

// IsInstalled checks if thegent is installed
func (b *Bridge) IsInstalled() bool {
	return b.thegentPath != ""
}

// GetConfig returns the bridge configuration path
func (b *Bridge) GetConfigPath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "phenotype", "bridge.toml")
}

// LoadConfig loads the bridge configuration
func (b *Bridge) LoadConfig() (BridgeConfig, error) {
	configPath := b.GetConfigPath()
	data, err := os.ReadFile(configPath)
	if err != nil {
		return DefaultConfig(), nil
	}

	var config BridgeConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return DefaultConfig(), err
	}

	return config, nil
}

// SaveConfig saves the bridge configuration
func (b *Bridge) SaveConfig(config BridgeConfig) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}

	configPath := b.GetConfigPath()
	os.MkdirAll(filepath.Dir(configPath), 0755)
	return os.WriteFile(configPath, data, 0644)
}
