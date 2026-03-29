package lib

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNVMSAuthHeader(t *testing.T) {
	t.Run("create NVMSAuthHeader struct", func(t *testing.T) {
		header := NVMSAuthHeader{
			PrivateKey: "private-key-123",
			PublicKey:  "public-key-456",
			BaseUrl:    "https://api.nvms.example.com",
		}

		assert.Equal(t, "private-key-123", header.PrivateKey)
		assert.Equal(t, "public-key-456", header.PublicKey)
		assert.Equal(t, "https://api.nvms.example.com", header.BaseUrl)
	})

	t.Run("empty NVMSAuthHeader struct", func(t *testing.T) {
		header := NVMSAuthHeader{}

		assert.Empty(t, header.PrivateKey)
		assert.Empty(t, header.PublicKey)
		assert.Empty(t, header.BaseUrl)
	})

	t.Run("partial NVMSAuthHeader struct", func(t *testing.T) {
		header := NVMSAuthHeader{
			PrivateKey: "only-private-key",
		}

		assert.Equal(t, "only-private-key", header.PrivateKey)
		assert.Empty(t, header.PublicKey)
		assert.Empty(t, header.BaseUrl)
	})

	t.Run("NVMSAuthHeader with special characters", func(t *testing.T) {
		header := NVMSAuthHeader{
			PrivateKey: "private-key-with-special-chars!@#$%^&*()",
			PublicKey:  "public-key-with-unicode-🔑",
			BaseUrl:    "https://api.example.com/v1/auth?param=value&other=test",
		}

		assert.Equal(t, "private-key-with-special-chars!@#$%^&*()", header.PrivateKey)
		assert.Equal(t, "public-key-with-unicode-🔑", header.PublicKey)
		assert.Equal(t, "https://api.example.com/v1/auth?param=value&other=test", header.BaseUrl)
	})

	t.Run("NVMSAuthHeader struct copy", func(t *testing.T) {
		original := NVMSAuthHeader{
			PrivateKey: "private-original",
			PublicKey:  "public-original",
			BaseUrl:    "https://original.com",
		}

		// Test that struct can be copied
		copy := original
		assert.Equal(t, original.PrivateKey, copy.PrivateKey)
		assert.Equal(t, original.PublicKey, copy.PublicKey)
		assert.Equal(t, original.BaseUrl, copy.BaseUrl)

		// Test that modifying copy doesn't affect original
		copy.PrivateKey = "private-modified"
		assert.NotEqual(t, original.PrivateKey, copy.PrivateKey)
		assert.Equal(t, "private-original", original.PrivateKey)
		assert.Equal(t, "private-modified", copy.PrivateKey)
	})

	t.Run("NVMSAuthHeader with long values", func(t *testing.T) {
		longKey := make([]byte, 1024)
		for i := range longKey {
			longKey[i] = 'a'
		}
		longKeyString := string(longKey)

		header := NVMSAuthHeader{
			PrivateKey: longKeyString,
			PublicKey:  longKeyString,
			BaseUrl:    "https://example.com/" + longKeyString,
		}

		assert.Equal(t, longKeyString, header.PrivateKey)
		assert.Equal(t, longKeyString, header.PublicKey)
		assert.Equal(t, "https://example.com/"+longKeyString, header.BaseUrl)
		assert.Equal(t, 1024, len(header.PrivateKey))
	})
}