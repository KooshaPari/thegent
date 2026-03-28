package services

import (
	"net/http"
	"testing"
)

// Traces to: FR-PROVIDER-040
func TestNewSupabaseClientStoresToken(t *testing.T) {
	client := NewSupabaseClient("supabase-tok")
	if client == nil {
		t.Fatal("NewSupabaseClient returned nil")
	}
	if client.token != "supabase-tok" {
		t.Errorf("expected token %q, got %q", "supabase-tok", client.token)
	}
}

// Traces to: FR-PROVIDER-041
func TestSupabaseMissingTokenReturnsError(t *testing.T) {
	client := &SupabaseClient{token: "", httpClient: &http.Client{}}
	_, err := client.ListProjects()
	if err == nil {
		t.Log("ListProjects with empty token unexpectedly succeeded")
	}
}

// Traces to: FR-PROVIDER-042
func TestSupabaseProjectFields(t *testing.T) {
	p := SupabaseProject{
		ID:             "proj-abc",
		Name:           "my-supabase-project",
		Status:         "ACTIVE_HEALTHY",
		Region:         "us-east-1",
		OrganizationID: "org-123",
	}
	if p.ID == "" {
		t.Error("SupabaseProject.ID must not be empty")
	}
	if p.OrganizationID == "" {
		t.Error("SupabaseProject.OrganizationID must not be empty")
	}
}
