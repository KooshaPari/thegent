package model

import "time"

type SessionMeta struct {
	ID           string            `json:"id"`
	Name         string            `json:"name"`
	Harness      string            `json:"harness"`
	Provider     string            `json:"provider"`
	Model        string            `json:"model"`
	Dir          string            `json:"dir"`
	CreatedAt    time.Time         `json:"created_at"`
	UpdatedAt    time.Time         `json:"updated_at"`
	UpdatedBy    string            `json:"updated_by"`
	LastMessage  string            `json:"last_message"`
	State        string            `json:"state"`
	ProviderMeta map[string]any    `json:"provider_meta"`
}
