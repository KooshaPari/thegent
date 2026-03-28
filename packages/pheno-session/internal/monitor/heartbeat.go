package monitor

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/KooshaPari/pheno-session/internal/sqlite"
)

// AgentStatus represents the status of a monitored agent
type AgentStatus struct {
	AgentID       string    `json:"agent_id"`
	Harness      string    `json:"harness"`
	PID          int       `json:"pid"`
	SessionID    string    `json:"session_id"`
	Command      string    `json:"command"`
	StartedAt    time.Time `json:"started_at"`
	LastCheckAt  time.Time `json:"last_check_at"`
	Status       string    `json:"status"` // running, stopped, stale, unknown
	CPUPercent   float64   `json:"cpu_percent"`
	MemoryMB     float64   `json:"memory_mb"`
	CurrentTask  string    `json:"current_task"`
}

// HeartbeatMonitor monitors all running agents across harnesses
type HeartbeatMonitor struct {
	store        *sqlite.UnifiedStore
	interval     time.Duration
	staleTimeout time.Duration
	stopChan     chan struct{}
	wg           sync.WaitGroup
	mu           sync.RWMutex
	agents       map[string]AgentStatus
}

// NewHeartbeatMonitor creates a new heartbeat monitor
func NewHeartbeatMonitor(store *sqlite.UnifiedStore, interval time.Duration) *HeartbeatMonitor {
	if interval == 0 {
		interval = 30 * time.Second
	}
	return &HeartbeatMonitor{
		store:        store,
		interval:     interval,
		staleTimeout: 5 * time.Minute,
		stopChan:     make(chan struct{}),
		agents:       make(map[string]AgentStatus),
	}
}

// Start begins monitoring
func (m *HeartbeatMonitor) Start() {
	m.wg.Add(1)
	go m.run()
}

// Stop stops monitoring
func (m *HeartbeatMonitor) Stop() {
	close(m.stopChan)
	m.wg.Wait()
}

func (m *HeartbeatMonitor) run() {
	defer m.wg.Done()
	
	ticker := time.NewTicker(m.interval)
	defer ticker.Stop()
	
	// Do initial scan
	m.scanAgents()
	
	for {
		select {
		case <-m.stopChan:
			return
		case <-ticker.C:
			m.scanAgents()
		}
	}
}

func (m *HeartbeatMonitor) scanAgents() {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	// Discover all running agents
	discovered := m.discoverRunningAgents()
	
	// Update store and track status
	for _, agent := range discovered {
		m.agents[agent.AgentID] = agent
		
		// Update in store
		runningAgent := sqlite.RunningAgent{
			AgentID:       agent.AgentID,
			Harness:       agent.Harness,
			SessionID:     agent.SessionID,
			PID:           agent.PID,
			StartedAt:     agent.StartedAt,
			LastHeartbeat: time.Now(),
			Status:        agent.Status,
			CurrentTask:   agent.CurrentTask,
		}
		
		// Try to update or create
		if err := m.store.UpdateRunningAgent(runningAgent); err != nil {
			// Agent might not exist, create it
			_ = m.store.CreateRunningAgent(runningAgent)
		}
		
		// Log heartbeat event
		m.logHeartbeat(agent)
	}
	
	// Mark stale agents
	for agentID, agent := range m.agents {
		found := false
		for _, discovered := range discovered {
			if discovered.AgentID == agentID {
				found = true
				break
			}
		}
		if !found {
			agent.Status = "stopped"
			m.agents[agentID] = agent
			
			// Log stopped event
			m.logAgentStopped(agent)
			
			// Delete from running agents in store
			_ = m.store.DeleteRunningAgent(agentID)
		}
	}
}

// discoverRunningAgents discovers all running agents across all harnesses
func (m *HeartbeatMonitor) discoverRunningAgents() []AgentStatus {
	var agents []AgentStatus
	
	// Discover based on harness patterns
	harnessPatterns := map[string][]string{
		"forge":   {"forge", "pheno-session", "claude-code"},
		"codex":  {"codex", "codex-agent", "claude"},
		"cursor":  {"cursor", "cursor-"},
		"claude":  {"claude-code", "anthropic"},
		"factory-droid": {"droid", "factory-droid"},
	}
	
	for harness, patterns := range harnessPatterns {
		for _, pattern := range patterns {
			found := m.discoverAgentsByPattern(harness, pattern)
			agents = append(agents, found...)
		}
	}
	
	return agents
}

// discoverAgentsByPattern finds agents matching a pattern
func (m *HeartbeatMonitor) discoverAgentsByPattern(harness, pattern string) []AgentStatus {
	var agents []AgentStatus
	
	// Use ps to find processes
	cmd := exec.Command("ps", "-eo", "pid,ppid,etime,command")
	output, err := cmd.Output()
	if err != nil {
		return agents
	}
	
	lines := strings.Split(string(output), "\n")
	for _, line := range lines[1:] { // Skip header
		if strings.Contains(line, pattern) && !strings.Contains(line, "grep") {
			agent := m.parseProcessLine(harness, line)
			if agent.AgentID != "" {
				agents = append(agents, agent)
			}
		}
	}
	
	return agents
}

// parseProcessLine parses a ps output line into AgentStatus
func (m *HeartbeatMonitor) parseProcessLine(harness, line string) AgentStatus {
	var agent AgentStatus
	
	fields := strings.Fields(line)
	if len(fields) < 4 {
		return agent
	}
	
	pid, err := strconv.Atoi(fields[0])
	if err != nil {
		return agent
	}
	
	// Get command
	command := strings.Join(fields[3:], " ")
	
	// Generate agent ID
	agent.AgentID = fmt.Sprintf("%s-%d", harness, pid)
	agent.Harness = harness
	agent.PID = pid
	agent.Command = command
	agent.Status = "running"
	agent.LastCheckAt = time.Now()
	
	// Parse elapsed time
	etime := fields[2]
	agent.StartedAt = m.parseElapsedTime(etime)
	
	// Get resource usage
	cpu, mem := m.getProcessResources(pid)
	agent.CPUPercent = cpu
	agent.MemoryMB = mem
	
	return agent
}

// parseElapsedTime converts elapsed time string to start time
func (m *HeartbeatMonitor) parseElapsedTime(etime string) time.Time {
	// Format can be: MM:SS, HH:MM:SS, or days-HH:MM:SS
	var hours, minutes, seconds int
	var days int
	
	parts := strings.Split(etime, "-")
	if len(parts) == 2 {
		// days-HH:MM:SS
		days, _ = strconv.Atoi(parts[0])
		timeParts := strings.Split(parts[1], ":")
		if len(timeParts) == 3 {
			hours, _ = strconv.Atoi(timeParts[0])
			minutes, _ = strconv.Atoi(timeParts[1])
			seconds, _ = strconv.Atoi(timeParts[2])
		}
	} else {
		timeParts := strings.Split(etime, ":")
		if len(timeParts) == 3 {
			hours, _ = strconv.Atoi(timeParts[0])
			minutes, _ = strconv.Atoi(timeParts[1])
			seconds, _ = strconv.Atoi(timeParts[2])
		} else if len(timeParts) == 2 {
			minutes, _ = strconv.Atoi(timeParts[0])
			seconds, _ = strconv.Atoi(timeParts[1])
		}
	}
	
	elapsed := time.Duration(days*24+hours)*time.Hour + time.Duration(minutes)*time.Minute + time.Duration(seconds)*time.Second
	return time.Now().Add(-elapsed)
}

// getProcessResources gets CPU and memory usage for a process
func (m *HeartbeatMonitor) getProcessResources(pid int) (float64, float64) {
	// Read process stats
	statFile := fmt.Sprintf("/proc/%d/stat", pid)
	data, err := os.ReadFile(statFile)
	if err != nil {
		return 0, 0
	}
	
	// Parse utime and stime
	fields := strings.Fields(string(data))
	if len(fields) < 24 {
		return 0, 0
	}
	
	utime, _ := strconv.ParseFloat(fields[13], 64)
	stime, _ := strconv.ParseFloat(fields[14], 64)
	
	// Calculate CPU percentage (simplified)
	cpuPercent := (utime + stime) / 100 // Rough approximation
	
	// Get memory
	memFile := fmt.Sprintf("/proc/%d/status", pid)
	memData, err := os.ReadFile(memFile)
	if err != nil {
		return cpuPercent, 0
	}
	
	re := regexp.MustCompile(`VmRSS:\s+(\d+)\s+kB`)
	matches := re.FindStringSubmatch(string(memData))
	if len(matches) > 1 {
		rss, _ := strconv.ParseFloat(matches[1], 64)
		return cpuPercent, rss / 1024 // Convert to MB
	}
	
	return cpuPercent, 0
}

// logHeartbeat logs a heartbeat event
func (m *HeartbeatMonitor) logHeartbeat(agent AgentStatus) {
	details, _ := json.Marshal(map[string]interface{}{
		"agent_id":     agent.AgentID,
		"harness":     agent.Harness,
		"pid":          agent.PID,
		"cpu_percent":  agent.CPUPercent,
		"memory_mb":    agent.MemoryMB,
		"current_task": agent.CurrentTask,
	})
	
	entry := sqlite.AuditLogEntry{
		AuditID:     fmt.Sprintf("heartbeat-%s-%d", agent.AgentID, time.Now().Unix()),
		Timestamp:   time.Now(),
		AgentID:     agent.AgentID,
		EventType:   "heartbeat",
		DetailsJSON: string(details),
	}
	
	_ = m.store.CreateAuditEntry(entry)
}

// logAgentStopped logs when an agent stops
func (m *HeartbeatMonitor) logAgentStopped(agent AgentStatus) {
	details, _ := json.Marshal(map[string]interface{}{
		"agent_id": agent.AgentID,
		"harness": agent.Harness,
		"pid":      agent.PID,
		"uptime":   time.Since(agent.StartedAt).String(),
	})
	
	entry := sqlite.AuditLogEntry{
		AuditID:     fmt.Sprintf("stopped-%s-%d", agent.AgentID, time.Now().Unix()),
		Timestamp:   time.Now(),
		AgentID:     agent.AgentID,
		EventType:   "agent_stopped",
		DetailsJSON: string(details),
	}
	
	_ = m.store.CreateAuditEntry(entry)
}

// GetAgents returns current agent statuses
func (m *HeartbeatMonitor) GetAgents() []AgentStatus {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	agents := make([]AgentStatus, 0, len(m.agents))
	for _, agent := range m.agents {
		agents = append(agents, agent)
	}
	return agents
}

// GetStaleAgents returns agents that haven't sent a heartbeat recently
func (m *HeartbeatMonitor) GetStaleAgents() []AgentStatus {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	var stale []AgentStatus
	for _, agent := range m.agents {
		if time.Since(agent.LastCheckAt) > m.staleTimeout {
			stale = append(stale, agent)
		}
	}
	return stale
}

// HarnessDiscovery discovers available harnesses
type HarnessDiscovery struct {
	Harness     string    `json:"harness"`
	Available   bool      `json:"available"`
	PID         int       `json:"pid"`
	SessionID   string    `json:"session_id"`
	LastSeen    time.Time `json:"last_seen"`
	Version     string    `json:"version"`
}

// DiscoverHarnesses discovers all available harnesses
func DiscoverHarnesses() []HarnessDiscovery {
	discoveries := []HarnessDiscovery{
		{Harness: "forge", Available: false},
		{Harness: "codex", Available: false},
		{Harness: "cursor", Available: false},
		{Harness: "claude", Available: false},
		{Harness: "factory-droid", Available: false},
	}
	
	// Check each harness
	harnessProcesses := map[string][]string{
		"forge":          {"forge", "pheno-session"},
		"codex":          {"codex", "codex-agent"},
		"cursor":         {"cursor"},
		"claude":         {"claude-code", "anthropic"},
		"factory-droid":  {"droid", "factory-droid"},
	}
	
	for i := range discoveries {
		patterns := harnessProcesses[discoveries[i].Harness]
		for _, pattern := range patterns {
			cmd := exec.Command("pgrep", "-f", pattern)
			output, err := cmd.Output()
			if err == nil && len(output) > 0 {
				lines := strings.Split(strings.TrimSpace(string(output)), "\n")
				if len(lines) > 0 {
					pid, _ := strconv.Atoi(lines[0])
					discoveries[i].Available = true
					discoveries[i].PID = pid
					discoveries[i].LastSeen = time.Now()
					
					// Try to get version
					version := getHarnessVersion(discoveries[i].Harness)
					discoveries[i].Version = version
					break
				}
			}
		}
	}
	
	return discoveries
}

// getHarnessVersion gets the version of a harness
func getHarnessVersion(harness string) string {
	cmd := exec.Command("which", harness)
	if cmd.Run() != nil {
		return "unknown"
	}
	
	switch harness {
	case "forge":
		cmd = exec.Command("forge", "--version")
	case "codex":
		cmd = exec.Command("codex", "--version")
	case "cursor":
		cmd = exec.Command("cursor", "--version")
	case "claude-code":
		cmd = exec.Command("claude", "--version")
	case "droid":
		cmd = exec.Command("droid", "--version")
	}
	
	output, err := cmd.Output()
	if err != nil {
		return "unknown"
	}
	
	return strings.TrimSpace(string(output))
}

// SessionScanner scans and imports sessions from all harnesses
type SessionScanner struct {
	store *sqlite.UnifiedStore
}

// NewSessionScanner creates a new session scanner
func NewSessionScanner(store *sqlite.UnifiedStore) *SessionScanner {
	return &SessionScanner{store: store}
}

// ScanAll scans all harnesses and imports sessions
func (s *SessionScanner) ScanAll() (int, error) {
	count := 0
	
	// Use adapter registry to discover sessions
	// For now, we'll scan common locations
	
	sessionLocations := map[string][]string{
		"forge": {
			os.Getenv("HOME") + "/.local/share/forge/sessions",
			os.Getenv("HOME") + "/.forge/sessions",
		},
		"codex": {
			os.Getenv("HOME") + "/.codex/sessions",
			os.Getenv("HOME") + "/Library/Application Support/Codex/sessions",
		},
		"cursor": {
			os.Getenv("HOME") + "/.cursor/data/sessions",
			os.Getenv("HOME") + "/Library/Application Support/Cursor/sessions",
		},
	}
	
	for harness, locations := range sessionLocations {
		for _, loc := range locations {
			scanned, err := s.scanDirectory(harness, loc)
			if err == nil {
				count += scanned
			}
		}
	}
	
	return count, nil
}

// scanDirectory scans a directory for session files
func (s *SessionScanner) scanDirectory(harness, dir string) (int, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 0, err
	}
	
	count := 0
	for _, entry := range entries {
		if entry.IsDir() {
			sessionFile := dir + "/" + entry.Name() + "/session.json"
			if data, err := os.ReadFile(sessionFile); err == nil {
				var session struct {
					ID        string `json:"id"`
					Name      string `json:"name"`
					Model     string `json:"model"`
					State     string `json:"state"`
					CreatedAt string `json:"created_at"`
					UpdatedAt string `json:"updated_at"`
				}
				if json.Unmarshal(data, &session) == nil {
					// Create session in store
					sess := sqlite.Session{
						ID:          session.ID,
						Harness:     harness,
						Model:       session.Model,
						State:       session.State,
						StartedAt:   time.Now(),
						IndexedAt:   time.Now(),
					}
					if err := s.store.CreateSession(sess); err == nil {
						count++
					}
				}
			}
		}
	}
	
	return count, nil
}
