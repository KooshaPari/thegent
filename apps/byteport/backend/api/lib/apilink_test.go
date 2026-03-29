package lib

import (
	"fmt"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

type httpDoFunc func(*http.Request) (*http.Response, error)

func (f httpDoFunc) Do(req *http.Request) (*http.Response, error) {
	return f(req)
}

func withHTTPDo(t *testing.T, fn func(*http.Request) (*http.Response, error), test func()) {
	t.Helper()
	original := httpDo
	httpDo = fn
	defer func() { httpDo = original }()
	test()
}

func TestValidatePortfolioAPI(t *testing.T) {
	withHTTPDo(t, func(req *http.Request) (*http.Response, error) {
		assert.Equal(t, "/byteport", req.URL.Path)
		assert.Equal(t, "Bearer test-key", req.Header.Get("Authorization"))
		return &http.Response{StatusCode: http.StatusOK, Body: http.NoBody, Header: make(http.Header)}, nil
	}, func() {
		err := ValidatePortfolioAPI("https://portfolio.example.com", "test-key")
		assert.NoError(t, err)
	})

	withHTTPDo(t, func(req *http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: http.StatusUnauthorized, Body: http.NoBody, Header: make(http.Header)}, nil
	}, func() {
		err := ValidatePortfolioAPI("https://portfolio.example.com", "bad-key")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "Status code: 401")
	})

	withHTTPDo(t, func(req *http.Request) (*http.Response, error) {
		return nil, fmt.Errorf("connection refused")
	}, func() {
		err := ValidatePortfolioAPI("https://portfolio.example.com", "test-key")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to connect")
	})

	err := ValidatePortfolioAPI("invalid-url", "test-key")
	assert.Error(t, err)
}

func TestValidateOpenAICredentials(t *testing.T) {
	withHTTPDo(t, func(req *http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: http.StatusUnauthorized, Body: http.NoBody, Header: make(http.Header)}, nil
	}, func() {
		err := ValidateOpenAICredentials("invalid-token")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "Status code: 401")
	})

	err := ValidateOpenAICredentials("")
	assert.Error(t, err)
}

func TestValidateAWSCredentials(t *testing.T) {
	err := ValidateAWSCredentials("", "secret")
	assert.Error(t, err)
}
