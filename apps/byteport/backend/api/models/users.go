package models

import (
	"time"

	"gorm.io/gorm"
)

type User struct {
	gorm.Model
	ID        string    `json:"id" gorm:"primaryKey"`
	Email     string    `json:"email" gorm:"uniqueIndex"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`

	// Provider credentials
	AWSCreds      *AWSCreds      `json:"awsCreds,omitempty" gorm:"embedded;embeddedPrefix:aws_"`
	VercelCreds   *VercelCreds   `json:"vercelCreds,omitempty" gorm:"embedded;embeddedPrefix:vercel_"`
	NetlifyCreds  *NetlifyCreds  `json:"netlifyCreds,omitempty" gorm:"embedded;embeddedPrefix:netlify_"`
	RailwayCreds  *RailwayCreds  `json:"railwayCreds,omitempty" gorm:"embedded;embeddedPrefix:railway_"`
	FlyIOCreds    *FlyIOCreds    `json:"flyioCreds,omitempty" gorm:"embedded;embeddedPrefix:flyio_"`
	SupabaseCreds *SupabaseCreds `json:"supabaseCreds,omitempty" gorm:"embedded;embeddedPrefix:supabase_"`
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
