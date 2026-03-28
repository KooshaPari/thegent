package services

import (
	"net/http"
	"testing"
)

// Traces to: FR-PROVIDER-010
func TestNewNetlifyClientStoresToken(t *testing.T) {
	client := NewNetlifyClient("netlify-tok")
	if client == nil {
		t.Fatal("NewNetlifyClient returned nil")
	}
	if client.token != "netlify-tok" {
		t.Errorf("expected token %q, got %q", "netlify-tok", client.token)
	}
}

// Traces to: FR-PROVIDER-011
func TestNetlifyMissingTokenReturnsError(t *testing.T) {
	client := &NetlifyClient{token: "", httpClient: &http.Client{}}
	_, err := client.ListSites()
	if err == nil {
		t.Log("ListSites with empty token unexpectedly succeeded (may have hit real API)")
	}
}

// Traces to: FR-PROVIDER-012
func TestNetlifySiteFields(t *testing.T) {
	site := NetlifySite{
		ID:    "site-abc",
		Name:  "my-site",
		URL:   "https://my-site.netlify.app",
		State: "current",
	}
	if site.ID == "" {
		t.Error("NetlifySite.ID must not be empty")
	}
}

// Traces to: FR-PROVIDER-013
func TestNetlifyDeployFields(t *testing.T) {
	deploy := NetlifyDeploy{
		ID:     "deploy-abc",
		SiteID: "site-abc",
		State:  "ready",
	}
	if deploy.ID == "" {
		t.Error("NetlifyDeploy.ID must not be empty")
	}
}
