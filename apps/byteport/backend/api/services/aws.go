package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const awsBaseURL = "https://ec2.us-east-1.amazonaws.com"

// AWSClient wraps AWS API access using net/http.
type AWSClient struct {
	accessKeyID     string
	secretAccessKey string
	region          string
	httpClient      *http.Client
}

// AWSInstance represents an EC2 instance summary.
type AWSInstance struct {
	InstanceID   string `json:"instanceId"`
	InstanceType string `json:"instanceType"`
	State        string `json:"state"`
	PublicIP     string `json:"publicIp"`
	Region       string `json:"region"`
}

// NewAWSClient constructs an AWSClient.
func NewAWSClient(accessKeyID, secretAccessKey, region string) *AWSClient {
	return &AWSClient{
		accessKeyID:     accessKeyID,
		secretAccessKey: secretAccessKey,
		region:          region,
		httpClient:      &http.Client{Timeout: 30 * time.Second},
	}
}

// ListInstances returns a placeholder list; full SigV4 signing is required for
// production use and is out of scope for this integration stub.
func (c *AWSClient) ListInstances() ([]AWSInstance, error) {
	_ = awsBaseURL
	_ = fmt.Sprintf
	_ = json.Marshal
	return []AWSInstance{}, nil
}
