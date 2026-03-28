package orchestration

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/KooshaPari/pheno-session/internal/adapter"
	"github.com/KooshaPari/pheno-session/internal/sqlite"
)

// MessageType represents the type of inter-agent message
type MessageType string

const (
	MessageTypeTask       MessageType = "task"
	MessageTypeStatus    MessageType = "status"
	MessageTypeResult    MessageType = "result"
	MessageTypeError     MessageType = "error"
	MessageTypeHeartbeat MessageType = "heartbeat"
	MessageTypeRequest   MessageType = "request"
	MessageTypeResponse  MessageType = "response"
)

// Message represents an inter-agent message
type Message struct {
	ID           string                 `json:"id"`
	FromAgent   string                 `json:"from_agent"`
	ToAgent     string                 `json:"to_agent"`
	Type        MessageType            `json:"type"`
	Subject     string                 `json:"subject"`
	Content     string                 `json:"content"`
	Priority    int                    `json:"priority"` // 1-5, 1 is highest
	SessionID   string                 `json:"session_id"`
	TaskID     string                 `json:"task_id"`
	Payload    map[string]interface{} `json:"payload"`
	SentAt     time.Time             `json:"sent_at"`
	ReceivedAt time.Time             `json:"received_at"`
	Acknowledged bool                 `json:"acknowledged"`
	Status     string                 `json:"status"` // pending, delivered, acknowledged, failed
}

// MessagingService handles inter-agent messaging
type MessagingService struct {
	store    *sqlite.UnifiedStore
	registry *adapter.AdapterRegistry
}

// NewMessagingService creates a new messaging service
func NewMessagingService(store *sqlite.UnifiedStore) *MessagingService {
	return &MessagingService{
		store:    store,
		registry: adapter.NewAdapterRegistry(),
	}
}

// SendMessage sends a message from one agent to another
func (s *MessagingService) SendMessage(fromAgent, toAgent string, msgType MessageType, subject, content string, priority int) (*Message, error) {
	if priority < 1 || priority > 5 {
		priority = 3
	}

	message := &Message{
		ID:         uuid.New().String(),
		FromAgent: fromAgent,
		ToAgent:   toAgent,
		Type:      msgType,
		Subject:   subject,
		Content:   content,
		Priority:  priority,
		SentAt:    time.Now(),
		Status:    "pending",
	}

	// Store in database
	dbMsg := sqlite.AgentMessage{
		MessageID:      message.ID,
		FromAgent:      message.FromAgent,
		ToAgent:        message.ToAgent,
		MessageType:    string(message.Type),
		PayloadJSON:    "",
		Priority:       message.Priority,
		SentAt:         message.SentAt,
		DeliveryStatus: message.Status,
	}

	if err := s.store.CreateMessage(dbMsg); err != nil {
		return nil, fmt.Errorf("failed to store message: %w", err)
	}

	// Try to deliver via harness adapter
	harness := extractHarness(toAgent)
	harnessAdapter := s.registry.Get(adapter.HarnessType(harness))

	if err := harnessAdapter.SendMessage(toAgent, s.formatMessage(message)); err != nil {
		message.Status = "failed"
		s.updateMessageStatus(message.ID, "failed")
		return message, fmt.Errorf("failed to deliver message: %w", err)
	}

	message.Status = "delivered"
	message.ReceivedAt = time.Now()
	s.updateMessageStatus(message.ID, "delivered")

	// Log event
	s.logMessageEvent("message_sent", message)

	return message, nil
}

// formatMessage formats a message for delivery
func (s *MessagingService) formatMessage(msg *Message) string {
	return fmt.Sprintf("[%s] %s: %s\n\n%s",
		msg.Type, msg.Subject, msg.FromAgent, msg.Content)
}

// updateMessageStatus updates the delivery status of a message
func (s *MessagingService) updateMessageStatus(messageID, status string) {
	// This would update the database - simplified for now
	_ = messageID
	_ = status
}

// SendTask sends a task to an agent
func (s *MessagingService) SendTask(fromAgent, toAgent, taskTitle, taskDescription string, priority int) (*Message, error) {
	return s.SendMessage(fromAgent, toAgent, MessageTypeTask, taskTitle, taskDescription, priority)
}

// SendStatusUpdate sends a status update to an agent
func (s *MessagingService) SendStatusUpdate(fromAgent, toAgent, status string) (*Message, error) {
	return s.SendMessage(fromAgent, toAgent, MessageTypeStatus, "Status Update", status, 3)
}

// SendResult sends a result to an agent
func (s *MessagingService) SendResult(fromAgent, toAgent, taskID, result string) (*Message, error) {
	return s.SendMessage(fromAgent, toAgent, MessageTypeResult, "Task Result: "+taskID, result, 1)
}

// SendError sends an error message to an agent
func (s *MessagingService) SendError(fromAgent, toAgent, errorMsg string) (*Message, error) {
	return s.SendMessage(fromAgent, toAgent, MessageTypeError, "Error", errorMsg, 1)
}

// BroadcastMessage broadcasts a message to all agents
func (s *MessagingService) BroadcastMessage(fromAgent string, msgType MessageType, subject, content string) ([]*Message, error) {
	var messages []*Message

	// Get all available agents
	agents, err := s.registry.DiscoverAllAgents()
	if err != nil {
		return nil, err
	}

	for _, agent := range agents {
		if agent.ID != fromAgent {
			msg, err := s.SendMessage(fromAgent, agent.ID, msgType, subject, content, 3)
			if err == nil {
				messages = append(messages, msg)
			}
		}
	}

	return messages, nil
}

// GetMessages retrieves messages for an agent
func (s *MessagingService) GetMessages(agentID string) ([]Message, error) {
	dbMessages, err := s.store.GetMessagesForAgent(agentID)
	if err != nil {
		return nil, err
	}

	messages := make([]Message, len(dbMessages))
	for i, m := range dbMessages {
		messages[i] = Message{
			ID:           m.MessageID,
			FromAgent:   m.FromAgent,
			ToAgent:     m.ToAgent,
			Type:        MessageType(m.MessageType),
			SessionID:   m.SessionID,
			Payload:     parsePayload(m.PayloadJSON),
			Priority:    m.Priority,
			SentAt:     m.SentAt,
			ReceivedAt: m.ReceivedAt,
			Acknowledged: m.Acknowledged,
			Status:     m.DeliveryStatus,
		}
	}

	return messages, nil
}

// GetUnreadMessages gets unread messages for an agent
func (s *MessagingService) GetUnreadMessages(agentID string) ([]Message, error) {
	messages, err := s.GetMessages(agentID)
	if err != nil {
		return nil, err
	}

	var unread []Message
	for _, msg := range messages {
		if !msg.Acknowledged && msg.Status == "delivered" {
			unread = append(unread, msg)
		}
	}

	return unread, nil
}

// AcknowledgeMessage acknowledges a message
func (s *MessagingService) AcknowledgeMessage(messageID string) error {
	return s.store.AcknowledgeMessage(messageID)
}

// ReplyTo sends a reply to the sender of a message
func (s *MessagingService) ReplyTo(original *Message, content string) (*Message, error) {
	return s.SendMessage(original.ToAgent, original.FromAgent, MessageTypeResponse,
		"Re: "+original.Subject, content, original.Priority)
}

// ForwardTo forwards a message to another agent
func (s *MessagingService) ForwardTo(original *Message, newRecipient string) (*Message, error) {
	content := fmt.Sprintf("Forwarded from %s:\n\n%s",
		original.FromAgent, original.Content)

	return s.SendMessage(original.ToAgent, newRecipient, original.Type,
		"Fwd: "+original.Subject, content, original.Priority)
}

// MessageSummary provides a summary of messages
type MessageSummary struct {
	Total     int            `json:"total"`
	Unread    int            `json:"unread"`
	ByType    map[string]int `json:"by_type"`
	ByAgent   map[string]int `json:"by_agent"`
}

// GetSummary returns a summary of messages for an agent
func (s *MessagingService) GetSummary(agentID string) (*MessageSummary, error) {
	messages, err := s.GetMessages(agentID)
	if err != nil {
		return nil, err
	}

	summary := &MessageSummary{
		Total:   len(messages),
		Unread:  0,
		ByType:  make(map[string]int),
		ByAgent: make(map[string]int),
	}

	for _, msg := range messages {
		if !msg.Acknowledged {
			summary.Unread++
		}

		summary.ByType[string(msg.Type)]++
		summary.ByAgent[msg.FromAgent]++
	}

	return summary, nil
}

// logMessageEvent logs a message event to the audit log
func (s *MessagingService) logMessageEvent(eventType string, msg *Message) {
	details := map[string]interface{}{
		"message_id": msg.ID,
		"from_agent": msg.FromAgent,
		"to_agent":   msg.ToAgent,
		"type":       msg.Type,
		"subject":    msg.Subject,
		"status":     msg.Status,
	}

	detailsJSON, _ := json.Marshal(details)

	entry := sqlite.AuditLogEntry{
		AuditID:     fmt.Sprintf("msg-%s-%d", msg.ID, time.Now().UnixNano()),
		Timestamp:   time.Now(),
		AgentID:     msg.FromAgent,
		SessionID:  msg.SessionID,
		EventType:  eventType,
		DetailsJSON: string(detailsJSON),
	}

	_ = s.store.CreateAuditEntry(entry)
}

// parsePayload parses a JSON payload
func parsePayload(payloadJSON string) map[string]interface{} {
	if payloadJSON == "" {
		return make(map[string]interface{})
	}

	var payload map[string]interface{}
	if err := json.Unmarshal([]byte(payloadJSON), &payload); err != nil {
		return make(map[string]interface{})
	}

	return payload
}

// MessageTemplate provides templates for common messages
type MessageTemplate struct {
	Type    MessageType
	Subject string
	Content string
}

// CommonMessageTemplates returns common message templates
func CommonMessageTemplates() []MessageTemplate {
	return []MessageTemplate{
		{MessageTypeTask, "New Task Assigned", "You have been assigned a new task. Please review and begin work."},
		{MessageTypeStatus, "Status Update Request", "Please provide a status update on your current task."},
		{MessageTypeRequest, "Information Request", "I need information about the current state of your work."},
		{MessageTypeResult, "Task Completed", "Your task has been completed successfully."},
		{MessageTypeError, "Error Report", "An error has occurred that requires your attention."},
	}
}

// QuickMessage creates a quick message using a template
func (s *MessagingService) QuickMessage(fromAgent, toAgent, templateName, customContent string) (*Message, error) {
	templates := map[string]MessageTemplate{
		"task":       {MessageTypeTask, "New Task", customContent},
		"status":     {MessageTypeStatus, "Status Update", customContent},
		"request":    {MessageTypeRequest, "Request", customContent},
		"result":     {MessageTypeResult, "Result", customContent},
		"error":      {MessageTypeError, "Error", customContent},
		"help":       {MessageTypeRequest, "Help Needed", customContent},
		"done":       {MessageTypeResult, "Task Done", customContent},
		"block":      {MessageTypeError, "Blocked", customContent},
		"progress":   {MessageTypeStatus, "Progress Update", customContent},
		"question":   {MessageTypeRequest, "Question", customContent},
	}

	if template, ok := templates[templateName]; ok {
		return s.SendMessage(fromAgent, toAgent, template.Type, template.Subject, template.Content, 3)
	}

	// Default to status update
	return s.SendMessage(fromAgent, toAgent, MessageTypeStatus, "Message", customContent, 3)
}

// MessageHistory returns the message history between two agents
func (s *MessagingService) MessageHistory(agent1, agent2 string, limit int) ([]Message, error) {
	messages, err := s.GetMessages(agent1)
	if err != nil {
		return nil, err
	}

	var history []Message
	for _, msg := range messages {
		if msg.FromAgent == agent2 || msg.ToAgent == agent2 {
			history = append(history, msg)
			if limit > 0 && len(history) >= limit {
				break
			}
		}
	}

	return history, nil
}

// formatMessagePreview returns a short preview of a message
func formatMessagePreview(msg *Message, maxLen int) string {
	preview := msg.Content
	if len(preview) > maxLen {
		preview = preview[:maxLen-3] + "..."
	}
	return strings.TrimSpace(preview)
}
