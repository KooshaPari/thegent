// Package domain contains the domain models for the config service.
package domain

import (
	"time"
)

// ConfigEntry represents a configuration key-value pair.
type ConfigEntry struct {
	ID          string    `json:"id"`
	Namespace   string    `json:"namespace"`
	Key         string    `json:"key"`
	Value       string    `json:"value"`
	ValueType   string    `json:"value_type"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	UpdatedBy   string    `json:"updated_by"`
	Description string    `json:"description,omitempty"`
}

// NewConfigEntry creates a new config entry.
func NewConfigEntry(namespace, key, value, valueType, updatedBy string) *ConfigEntry {
	now := time.Now().UTC()
	return &ConfigEntry{
		ID:          generateID(),
		Namespace:   namespace,
		Key:         key,
		Value:       value,
		ValueType:   valueType,
		CreatedAt:   now,
		UpdatedAt:   now,
		UpdatedBy:   updatedBy,
		Description: "",
	}
}

// Update updates the config entry value.
func (c *ConfigEntry) Update(value string, updatedBy string) {
	c.Value = value
	c.UpdatedAt = time.Now().UTC()
	c.UpdatedBy = updatedBy
}

// Validate validates the config entry.
func (c *ConfigEntry) Validate() error {
	if c.Key == "" {
		return ErrKeyRequired
	}
	if c.ValueType == "" {
		c.ValueType = "string"
	}
	if !isValidValueType(c.ValueType) {
		return ErrInvalidValueType
	}
	return nil
}

// ValueType constants.
const (
	ValueTypeString   = "string"
	ValueTypeNumber   = "number"
	ValueTypeBoolean  = "boolean"
	ValueTypeJSON     = "json"
	ValueTypeBase64   = "base64"
)

var validValueTypes = map[string]bool{
	ValueTypeString:  true,
	ValueTypeNumber:  true,
	ValueTypeBoolean: true,
	ValueTypeJSON:    true,
	ValueTypeBase64:  true,
}

func isValidValueType(t string) bool {
	return validValueTypes[t]
}

// Simple ID generation (in production, use UUID or similar).
func generateID() string {
	return fmt.Sprintf("cfg_%d", time.Now().UnixNano())
}

import "fmt"
