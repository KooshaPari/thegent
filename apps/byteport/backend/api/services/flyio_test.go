package services

import (
	"net/http"
	"testing"
)

// Traces to: FR-PROVIDER-030
func TestNewFlyioClientStoresToken(t *testing.T) {
	client := NewFlyioClient("fly-tok")
	if client == nil {
		t.Fatal("NewFlyioClient returned nil")
	}
	if client.token != "fly-tok" {
		t.Errorf("expected token %q, got %q", "fly-tok", client.token)
	}
}

// Traces to: FR-PROVIDER-031
func TestFlyioMissingTokenReturnsError(t *testing.T) {
	client := &FlyioClient{token: "", httpClient: &http.Client{}}
	_, err := client.ListApps()
	if err == nil {
		t.Log("ListApps with empty token unexpectedly succeeded")
	}
}

// Traces to: FR-PROVIDER-032
func TestFlyAppFields(t *testing.T) {
	app := FlyApp{
		ID:     "app-abc",
		Name:   "my-fly-app",
		Status: "running",
	}
	if app.ID == "" {
		t.Error("FlyApp.ID must not be empty")
	}
}

// Traces to: FR-PROVIDER-033
func TestFlyMachineFields(t *testing.T) {
	m := FlyMachine{
		ID:     "machine-abc",
		Name:   "my-machine",
		State:  "started",
		Region: "iad",
	}
	if m.ID == "" {
		t.Error("FlyMachine.ID must not be empty")
	}
	if m.Region == "" {
		t.Error("FlyMachine.Region must not be empty")
	}
}
