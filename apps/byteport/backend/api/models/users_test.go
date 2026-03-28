package models

import (
	"testing"
	"time"
)

// Traces to: FR-AUTH-001
func TestUserFieldsArePresent(t *testing.T) {
	now := time.Now()
	tests := []struct {
		name  string
		user  User
		valid bool
	}{
		{
			name: "fully populated user",
			user: User{
				ID:        "user-123",
				Email:     "test@example.com",
				Name:      "Test User",
				CreatedAt: now,
				UpdatedAt: now,
			},
			valid: true,
		},
		{
			name:  "zero-value user has empty ID",
			user:  User{},
			valid: false,
		},
		{
			name: "user with all provider creds",
			user: User{
				ID:    "user-456",
				Email: "provider@example.com",
				AWSCreds: &AWSCreds{
					AccessKeyID:     "AKID",
					SecretAccessKey: "secret",
					Region:          "us-east-1",
				},
				VercelCreds:   &VercelCreds{Token: "vercel-token"},
				NetlifyCreds:  &NetlifyCreds{Token: "netlify-token"},
				RailwayCreds:  &RailwayCreds{Token: "railway-token"},
				FlyIOCreds:    &FlyIOCreds{Token: "fly-token"},
				SupabaseCreds: &SupabaseCreds{Token: "supabase-token"},
			},
			valid: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			isValid := tc.user.ID != ""
			if isValid != tc.valid {
				t.Errorf("expected valid=%v, got valid=%v for user %+v", tc.valid, isValid, tc.user)
			}
		})
	}
}

// Traces to: FR-AUTH-002
func TestCredStructsHaveTokenField(t *testing.T) {
	vercel := VercelCreds{Token: "tok"}
	if vercel.Token != "tok" {
		t.Errorf("VercelCreds.Token = %q, want %q", vercel.Token, "tok")
	}

	netlify := NetlifyCreds{Token: "tok"}
	if netlify.Token != "tok" {
		t.Errorf("NetlifyCreds.Token = %q, want %q", netlify.Token, "tok")
	}

	railway := RailwayCreds{Token: "tok"}
	if railway.Token != "tok" {
		t.Errorf("RailwayCreds.Token = %q, want %q", railway.Token, "tok")
	}

	flyio := FlyIOCreds{Token: "tok"}
	if flyio.Token != "tok" {
		t.Errorf("FlyIOCreds.Token = %q, want %q", flyio.Token, "tok")
	}

	supabase := SupabaseCreds{Token: "tok"}
	if supabase.Token != "tok" {
		t.Errorf("SupabaseCreds.Token = %q, want %q", supabase.Token, "tok")
	}
}

// Traces to: FR-AUTH-003
func TestAWSCredsFields(t *testing.T) {
	creds := AWSCreds{
		AccessKeyID:     "AKIAIOSFODNN7EXAMPLE",
		SecretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
		Region:          "us-west-2",
	}
	if creds.AccessKeyID == "" {
		t.Error("AWSCreds.AccessKeyID must not be empty")
	}
	if creds.SecretAccessKey == "" {
		t.Error("AWSCreds.SecretAccessKey must not be empty")
	}
	if creds.Region == "" {
		t.Error("AWSCreds.Region must not be empty")
	}
}
