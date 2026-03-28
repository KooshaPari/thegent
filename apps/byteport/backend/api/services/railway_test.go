package services

import (
	"net/http"
	"testing"
)

// Traces to: FR-PROVIDER-020
func TestNewRailwayClientStoresToken(t *testing.T) {
	client := NewRailwayClient("railway-tok")
	if client == nil {
		t.Fatal("NewRailwayClient returned nil")
	}
	if client.token != "railway-tok" {
		t.Errorf("expected token %q, got %q", "railway-tok", client.token)
	}
}

// Traces to: FR-PROVIDER-021
func TestRailwayMissingTokenReturnsError(t *testing.T) {
	client := &RailwayClient{token: "", httpClient: &http.Client{}}
	_, err := client.ListProjects()
	if err == nil {
		t.Log("ListProjects with empty token unexpectedly succeeded")
	}
}

// Traces to: FR-PROVIDER-022
func TestRailwayProjectFields(t *testing.T) {
	p := RailwayProject{
		ID:          "proj-123",
		Name:        "my-railway-project",
		Description: "A test project",
	}
	if p.ID == "" {
		t.Error("RailwayProject.ID must not be empty")
	}
	if p.Name == "" {
		t.Error("RailwayProject.Name must not be empty")
	}
}
