package lib

import (
	"fmt"
	"io"
	"net/http"
)

var httpDo = func(req *http.Request) (*http.Response, error) {
	return http.DefaultClient.Do(req)
}

// ValidatePortfolioAPI validates the provided portfolio API key and endpoint.
func ValidatePortfolioAPI(rootEndpoint, apiKey string) error {
	fmt.Println("Validating Portfolio API...")
	fmt.Println("URI: " + rootEndpoint + "/byteport")
	req, err := http.NewRequest("GET", rootEndpoint+"/byteport", nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+apiKey)

	resp, err := httpDo(req)
	if err != nil {
		return fmt.Errorf("failed to connect to Portfolio API: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response body: %v", err)
	}
	fmt.Printf("Portfolio API Response: %s\n", string(body))

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("invalid Portfolio API Key or URL. Status code: %d", resp.StatusCode)
	}

	fmt.Println("Portfolio API validated successfully.")
	return nil
}

// ValidateOpenAICompatCredentials validates any OpenAI-compatible API endpoint.
// For Ollama, pass baseURL = "http://localhost:11434" and apiToken = "".
// wraps: OpenAI-compatible /v1/models endpoint
func ValidateOpenAICompatCredentials(baseURL, apiToken string) error {
	if baseURL == "" {
		baseURL = "https://api.openai.com"
	}
	fmt.Println("Validating LLM credentials at", baseURL)
	req, err := http.NewRequest("GET", baseURL+"/v1/models", nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	if apiToken != "" {
		req.Header.Set("Authorization", "Bearer "+apiToken)
	}

	resp, err := httpDo(req)
	if err != nil {
		return fmt.Errorf("failed to connect to LLM API: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read LLM response: %v", err)
	}
	fmt.Printf("LLM API Response: %s\n", string(body))

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("invalid LLM API credentials. Status code: %d", resp.StatusCode)
	}

	fmt.Println("LLM credentials validated successfully.")
	return nil
}

// ValidateOpenAICredentials is kept for call-site compatibility.
// It delegates to ValidateOpenAICompatCredentials using the OpenAI base URL.
//
// Deprecated: prefer ValidateOpenAICompatCredentials with an explicit baseURL,
// or use clients.CredentialValidator.ValidateOllamaCredentials for Ollama.
func ValidateOpenAICredentials(apiToken string) error {
	return ValidateOpenAICompatCredentials("https://api.openai.com", apiToken)
}

// ValidateAWSCredentials is a lightweight stub that accepts non-empty credentials
// without making a network call. The AWS SDK has been removed as a compile-time
// dependency. For production AWS credential validation, callers should use
// clients.CredentialValidator.ValidateAWSCredentials which can be extended with
// the AWS SDK via an optional build tag.
func ValidateAWSCredentials(accessKey, secretKey string) error {
	if accessKey == "" {
		return fmt.Errorf("AWS access key ID is required")
	}
	if secretKey == "" {
		return fmt.Errorf("AWS secret access key is required")
	}
	fmt.Println("AWS credentials present (format validation only — AWS SDK removed).")
	return nil
}
