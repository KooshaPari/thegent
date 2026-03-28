package models

import (
	"time"
)

type User struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`

	// Provider credentials
	AWSCreds      *AWSCreds      `json:"awsCreds,omitempty"`
	VercelCreds   *VercelCreds   `json:"vercelCreds,omitempty"`
	NetlifyCreds  *NetlifyCreds  `json:"netlifyCreds,omitempty"`
	RailwayCreds  *RailwayCreds  `json:"railwayCreds,omitempty"`
	FlyIOCreds    *FlyIOCreds    `json:"flyioCreds,omitempty"`
	SupabaseCreds *SupabaseCreds `json:"supabaseCreds,omitempty"`
}

type AWSCreds struct {
	AccessKeyID     string `json:"accessKeyId"`
	SecretAccessKey string `json:"secretAccessKey"`
	Region          string `json:"region"`
}

type VercelCreds struct {
	Token string `json:"token"`
}

type NetlifyCreds struct {
	Token string `json:"token"`
}

type RailwayCreds struct {
	Token string `json:"token"`
}

type FlyIOCreds struct {
	Token string `json:"token"`
}

type SupabaseCreds struct {
	Token string `json:"token"`
}
