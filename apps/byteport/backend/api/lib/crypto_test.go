package lib

import (
	"encoding/base64"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/byteport/api/models"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEncryptPass(t *testing.T) {
	password := "testpassword123"
	hash := EncryptPass(password)

	assert.NotEmpty(t, hash)
	assert.True(t, strings.HasPrefix(hash, "$argon2id$"))
	assert.Contains(t, hash, "v=19") // Argon2 version

	// Test that same password produces different hashes (due to random salt)
	hash2 := EncryptPass(password)
	assert.NotEqual(t, hash, hash2)
}

func TestValidatePass(t *testing.T) {
	password := "testpassword123"
	wrongPassword := "wrongpassword"

	// Generate hash
	hash := EncryptPass(password)

	// Test correct password
	isValid := ValidatePass(password, hash)
	assert.True(t, isValid)

	// Test wrong password
	isValid = ValidatePass(wrongPassword, hash)
	assert.False(t, isValid)

	// Test empty password
	isValid = ValidatePass("", hash)
	assert.False(t, isValid)
}

func TestGenerateFromPassword(t *testing.T) {
	password := "testpassword"
	params := &params{
		memory:      64 * 1024,
		iterations:  3,
		parallelism: 2,
		saltLength:  16,
		keyLength:   32,
	}

	hash, err := generateFromPassword(password, params)
	assert.NoError(t, err)
	assert.NotEmpty(t, hash)
	assert.True(t, strings.HasPrefix(hash, "$argon2id$"))

	// Verify the hash contains expected parameters
	assert.Contains(t, hash, "m=65536")
	assert.Contains(t, hash, "t=3")
	assert.Contains(t, hash, "p=2")
}

func TestGenerateRandomBytes(t *testing.T) {
	// Test different lengths
	lengths := []uint32{16, 32, 64}

	for _, length := range lengths {
		bytes, err := generateRandomBytes(length)
		assert.NoError(t, err)
		assert.Equal(t, int(length), len(bytes))

		// Test that multiple calls produce different results
		bytes2, err := generateRandomBytes(length)
		assert.NoError(t, err)
		assert.NotEqual(t, bytes, bytes2)
	}

	// Test zero length
	bytes, err := generateRandomBytes(0)
	assert.NoError(t, err)
	assert.Equal(t, 0, len(bytes))
}

func TestComparePasswordAndHash(t *testing.T) {
	password := "testpassword123"
	params := &params{
		memory:      64 * 1024,
		iterations:  3,
		parallelism: 2,
		saltLength:  16,
		keyLength:   32,
	}

	hash, err := generateFromPassword(password, params)
	require.NoError(t, err)

	// Test correct password
	match, err := comparePasswordAndHash(password, hash)
	assert.NoError(t, err)
	assert.True(t, match)

	// Test wrong password
	match, err = comparePasswordAndHash("wrongpassword", hash)
	assert.NoError(t, err)
	assert.False(t, match)

	// Test empty password
	match, err = comparePasswordAndHash("", hash)
	assert.NoError(t, err)
	assert.False(t, match)
}

func TestDecodeHash(t *testing.T) {
	// Test valid hash
	validHash := "$argon2id$v=19$m=65536,t=3,p=2$c2FsdA$aGFzaA"
	params, salt, hash, err := decodeHash(validHash)
	assert.NoError(t, err)
	assert.NotNil(t, params)
	assert.Equal(t, uint32(65536), params.memory)
	assert.Equal(t, uint32(3), params.iterations)
	assert.Equal(t, uint8(2), params.parallelism)
	assert.NotEmpty(t, salt)
	assert.NotEmpty(t, hash)

	// Test invalid hash format - not enough parts
	invalidHash := "$argon2id$v=19$m=65536"
	_, _, _, err = decodeHash(invalidHash)
	assert.Error(t, err)
	assert.Equal(t, ErrInvalidHash, err)

	// Test invalid version
	invalidVersionHash := "$argon2id$v=18$m=65536,t=3,p=2$c2FsdA$aGFzaA"
	_, _, _, err = decodeHash(invalidVersionHash)
	assert.Error(t, err)
	assert.Equal(t, ErrIncompatibleVersion, err)

	// Test invalid base64 encoding
	invalidBase64Hash := "$argon2id$v=19$m=65536,t=3,p=2$invalid!@#$aGFzaA"
	_, _, _, err = decodeHash(invalidBase64Hash)
	assert.Error(t, err)
}

func TestGetDecodedEncryptionKey(t *testing.T) {
	// Test with no key set
	os.Unsetenv("ENCRYPTION_KEY")
	_, err := GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "encryption key is not set")

	// Test with valid 32-byte key
	validKey := base64.StdEncoding.EncodeToString([]byte("12345678901234567890123456789012"))
	os.Setenv("ENCRYPTION_KEY", validKey)
	decodedKey, err := GetDecodedEncryptionKey()
	assert.NoError(t, err)
	assert.Equal(t, 32, len(decodedKey))

	// Test with valid 16-byte key
	validKey16 := base64.StdEncoding.EncodeToString([]byte("1234567890123456"))
	os.Setenv("ENCRYPTION_KEY", validKey16)
	decodedKey, err = GetDecodedEncryptionKey()
	assert.NoError(t, err)
	assert.Equal(t, 16, len(decodedKey))

	// Test with valid 24-byte key
	validKey24 := base64.StdEncoding.EncodeToString([]byte("123456789012345678901234"))
	os.Setenv("ENCRYPTION_KEY", validKey24)
	decodedKey, err = GetDecodedEncryptionKey()
	assert.NoError(t, err)
	assert.Equal(t, 24, len(decodedKey))

	// Test with invalid key length
	invalidKey := base64.StdEncoding.EncodeToString([]byte("short"))
	os.Setenv("ENCRYPTION_KEY", invalidKey)
	_, err = GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid key length")

	// Test with invalid base64
	os.Setenv("ENCRYPTION_KEY", "not-base64!@#$")
	_, err = GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode encryption key")

	// Test with whitespace
	keyWithWhitespace := "  " + validKey + "  "
	os.Setenv("ENCRYPTION_KEY", keyWithWhitespace)
	decodedKey, err = GetDecodedEncryptionKey()
	assert.NoError(t, err)
	assert.Equal(t, 32, len(decodedKey))

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestEncryptDecryptSecret(t *testing.T) {
	// Set up valid encryption key
	validKey := base64.StdEncoding.EncodeToString([]byte("12345678901234567890123456789012"))
	os.Setenv("ENCRYPTION_KEY", validKey)
	defer os.Unsetenv("ENCRYPTION_KEY")

	secret := "my-secret-data"

	// Test encryption
	encryptedSecret, err := EncryptSecret(secret)
	assert.NoError(t, err)
	assert.NotEmpty(t, encryptedSecret)
	assert.NotEqual(t, secret, encryptedSecret)

	// Test decryption
	decryptedSecret, err := DecryptSecret(encryptedSecret)
	assert.NoError(t, err)
	assert.Equal(t, secret, decryptedSecret)

	// Test encryption produces different results each time (due to IV)
	encryptedSecret2, err := EncryptSecret(secret)
	assert.NoError(t, err)
	assert.NotEqual(t, encryptedSecret, encryptedSecret2)

	// But both should decrypt to the same secret
	decryptedSecret2, err := DecryptSecret(encryptedSecret2)
	assert.NoError(t, err)
	assert.Equal(t, secret, decryptedSecret2)
}

func TestEncryptSecretWithInvalidKey(t *testing.T) {
	// Test with no key
	os.Unsetenv("ENCRYPTION_KEY")
	_, err := EncryptSecret("test")
	assert.Error(t, err)

	// Test with invalid key length
	invalidKey := base64.StdEncoding.EncodeToString([]byte("short"))
	os.Setenv("ENCRYPTION_KEY", invalidKey)
	defer os.Unsetenv("ENCRYPTION_KEY")

	_, err = EncryptSecret("test")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid key length")
}

func TestDecryptSecretWithInvalidData(t *testing.T) {
	// Set up valid encryption key
	validKey := base64.StdEncoding.EncodeToString([]byte("12345678901234567890123456789012"))
	os.Setenv("ENCRYPTION_KEY", validKey)
	defer os.Unsetenv("ENCRYPTION_KEY")

	// Test with invalid base64
	_, err := DecryptSecret("invalid-base64!@#$")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode base64")

	// Test with data too short (less than AES block size)
	shortData := base64.StdEncoding.EncodeToString([]byte("short"))
	_, err = DecryptSecret(shortData)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "ciphertext too short")

	// Test with no key
	os.Unsetenv("ENCRYPTION_KEY")
	_, err = DecryptSecret("some-encrypted-data")
	assert.Error(t, err)

	// Test with invalid key length
	invalidKey := base64.StdEncoding.EncodeToString([]byte("short"))
	os.Setenv("ENCRYPTION_KEY", invalidKey)
	_, err = DecryptSecret("some-encrypted-data")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid key length")
}

func TestGenerateEncryptionKey(t *testing.T) {
	key, err := GenerateEncryptionKey()
	assert.NoError(t, err)
	assert.NotEmpty(t, key)

	// Decode and verify length
	decodedKey, err := base64.StdEncoding.DecodeString(key)
	assert.NoError(t, err)
	assert.Equal(t, 32, len(decodedKey))

	// Generate another key to ensure they're different
	key2, err := GenerateEncryptionKey()
	assert.NoError(t, err)
	assert.NotEqual(t, key, key2)
}

func TestSetEncryptionKeyEnvVar(t *testing.T) {
	key := "test-encryption-key"

	err := SetEncryptionKeyEnvVar(key)
	assert.NoError(t, err)

	retrievedKey := os.Getenv("ENCRYPTION_KEY")
	assert.Equal(t, key, retrievedKey)

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestInitializeEncryptionKey(t *testing.T) {
	// Test when key doesn't exist
	os.Unsetenv("ENCRYPTION_KEY")

	err := InitializeEncryptionKey()
	assert.NoError(t, err)

	// Verify key was set
	key := os.Getenv("ENCRYPTION_KEY")
	assert.NotEmpty(t, key)

	// Verify it's a valid base64-encoded 32-byte key
	decodedKey, err := base64.StdEncoding.DecodeString(key)
	assert.NoError(t, err)
	assert.Equal(t, 32, len(decodedKey))

	// Test when key already exists
	existingKey := key
	err = InitializeEncryptionKey()
	assert.NoError(t, err)

	// Key should remain the same
	currentKey := os.Getenv("ENCRYPTION_KEY")
	assert.Equal(t, existingKey, currentKey)

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestPersistEncryptionKey(t *testing.T) {
	// This test is tricky because it modifies .zshrc
	// We'll test the function but not actually write to the real file

	key := "test-key-123"

	// Test that the function exists and handles basic cases
	// In a real scenario, you might want to use a temporary file
	// or mock the file operations

	// For now, we'll just verify the function signature and basic error handling
	// by testing with a non-existent file path
	originalHome := os.Getenv("HOME")
	os.Setenv("HOME", "/nonexistent/path")

	err := PersistEncryptionKey(key)
	assert.Error(t, err) // Should fail because path doesn't exist

	// Restore original HOME
	os.Setenv("HOME", originalHome)
}

func TestErrorConstants(t *testing.T) {
	assert.Equal(t, "the encoded hash is not in the correct format", ErrInvalidHash.Error())
	assert.Equal(t, "incompatible version of argon2", ErrIncompatibleVersion.Error())
}

func TestCompleteEncryptDecryptFlow(t *testing.T) {
	// Initialize encryption key
	err := InitializeEncryptionKey()
	require.NoError(t, err)

	testSecrets := []string{
		"simple-secret",
		"complex-secret-with-special-chars!@#$%^&*()",
		"very-long-secret-" + strings.Repeat("data", 100),
		"", // empty secret
		"unicode-secret-🔐🗝️",
	}

	for _, secret := range testSecrets {
		t.Run("secret-length-"+string(rune(len(secret))), func(t *testing.T) {
			encrypted, err := EncryptSecret(secret)
			assert.NoError(t, err)

			decrypted, err := DecryptSecret(encrypted)
			assert.NoError(t, err)
			assert.Equal(t, secret, decrypted)
		})
	}

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestCompletePasswordFlow(t *testing.T) {
	passwords := []string{
		"simple",
		"Complex123!",
		"very-long-password-" + strings.Repeat("chars", 50),
		"unicode-password-🔐",
	}

	for _, password := range passwords {
		t.Run("password-"+password[:min(len(password), 10)], func(t *testing.T) {
			hash := EncryptPass(password)
			assert.NotEmpty(t, hash)

			// Validate correct password
			isValid := ValidatePass(password, hash)
			assert.True(t, isValid)

			// Validate wrong password
			isValid = ValidatePass(password+"wrong", hash)
			assert.False(t, isValid)
		})
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Additional tests for better coverage

func TestDecodeHashErrors(t *testing.T) {
	// Test invalid hash format with wrong number of parts
	_, _, _, err := decodeHash("invalid")
	assert.Error(t, err)
	assert.Equal(t, ErrInvalidHash, err)

	// Test invalid version format
	_, _, _, err = decodeHash("$argon2id$invalid$m=64,t=3,p=2$salt$hash")
	assert.Error(t, err)

	// Test incompatible version
	_, _, _, err = decodeHash("$argon2id$v=99$m=64,t=3,p=2$salt$hash")
	assert.Error(t, err)
	assert.Equal(t, ErrIncompatibleVersion, err)

	// Test invalid parameters format
	_, _, _, err = decodeHash("$argon2id$v=19$invalid$salt$hash")
	assert.Error(t, err)

	// Test invalid base64 salt
	_, _, _, err = decodeHash("$argon2id$v=19$m=64,t=3,p=2$invalid!!!$hash")
	assert.Error(t, err)

	// Test invalid base64 hash
	_, _, _, err = decodeHash("$argon2id$v=19$m=64,t=3,p=2$c2FsdA$invalid!!!")
	assert.Error(t, err)
}

func TestGenerateRandomBytesError(t *testing.T) {
	// Test successful generation
	bytes, err := generateRandomBytes(16)
	assert.NoError(t, err)
	assert.Len(t, bytes, 16)

	// Test zero length
	bytes, err = generateRandomBytes(0)
	assert.NoError(t, err)
	assert.Len(t, bytes, 0)
}

func TestEncryptDecryptErrors(t *testing.T) {
	// Setup a valid encryption key first
	err := InitializeEncryptionKey()
	require.NoError(t, err)

	// Test DecryptSecret with invalid base64
	_, err = DecryptSecret("invalid-base64!!!")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode base64")

	// Test DecryptSecret with ciphertext too short
	_, err = DecryptSecret(base64.StdEncoding.EncodeToString([]byte("short")))
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "ciphertext too short")

	// Test EncryptSecret and DecryptSecret without encryption key
	os.Unsetenv("ENCRYPTION_KEY")
	_, err = EncryptSecret("test-secret")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "encryption key is not set")

	_, err = DecryptSecret("some-ciphertext")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "encryption key is not set")

	// Test with invalid base64 encryption key
	os.Setenv("ENCRYPTION_KEY", "invalid-base64!!!")
	_, err = EncryptSecret("test-secret")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode encryption key")

	// Test with wrong key length (set valid base64 but wrong length)
	shortKey := base64.StdEncoding.EncodeToString([]byte("short"))
	os.Setenv("ENCRYPTION_KEY", shortKey)
	_, err = EncryptSecret("test-secret")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid key length")

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestGetDecodedEncryptionKeyErrors(t *testing.T) {
	// Test when key is not set
	os.Unsetenv("ENCRYPTION_KEY")
	_, err := GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "encryption key is not set")

	// Test with invalid base64
	os.Setenv("ENCRYPTION_KEY", "invalid-base64!!!")
	_, err = GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode encryption key")

	// Test with invalid key length
	shortKey := base64.StdEncoding.EncodeToString([]byte("short"))
	os.Setenv("ENCRYPTION_KEY", shortKey)
	_, err = GetDecodedEncryptionKey()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid key length")

	// Test with key that has whitespace (should be trimmed)
	validKey := base64.StdEncoding.EncodeToString(make([]byte, 32))
	os.Setenv("ENCRYPTION_KEY", "  "+validKey+"  ")
	key, err := GetDecodedEncryptionKey()
	assert.NoError(t, err)
	assert.Len(t, key, 32)

	// Clean up
	os.Unsetenv("ENCRYPTION_KEY")
}

func TestPersistEncryptionKeySuccess(t *testing.T) {
	// Create a temporary file to simulate .zshrc
	tmpFile, err := os.CreateTemp("", "test_zshrc")
	require.NoError(t, err)
	defer os.Remove(tmpFile.Name())
	defer tmpFile.Close()

	// Set HOME to point to a directory containing our temp file
	tmpDir := os.TempDir()
	tmpZshrc := tmpDir + "/.zshrc"
	err = os.Rename(tmpFile.Name(), tmpZshrc)
	require.NoError(t, err)
	defer os.Remove(tmpZshrc)

	originalHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", originalHome)

	// Test successful persistence
	testKey := "test-encryption-key-123"
	err = PersistEncryptionKey(testKey)
	assert.NoError(t, err)

	// Verify the key was written to the file
	content, err := os.ReadFile(tmpZshrc)
	assert.NoError(t, err)
	assert.Contains(t, string(content), `export ENCRYPTION_KEY="test-encryption-key-123"`)
}

func TestPersistEncryptionKeyFileErrors(t *testing.T) {
	// Test with non-existent directory
	originalHome := os.Getenv("HOME")
	os.Setenv("HOME", "/nonexistent/directory")
	defer os.Setenv("HOME", originalHome)

	err := PersistEncryptionKey("test-key")
	assert.Error(t, err) // Should fail to open non-existent file

	// Test with directory that exists but file doesn't have write permissions
	tmpDir, err := os.MkdirTemp("", "test_home")
	require.NoError(t, err)
	defer os.RemoveAll(tmpDir)

	// Create a .zshrc file with no write permissions
	zshrcPath := tmpDir + "/.zshrc"
	err = os.WriteFile(zshrcPath, []byte("# existing content\n"), 0444) // read-only
	require.NoError(t, err)

	os.Setenv("HOME", tmpDir)
	err = PersistEncryptionKey("test-key")
	assert.Error(t, err) // Should fail due to permissions
}

// Additional auth function tests for better coverage

func TestInitAuthSystemErrors(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	// Clean up existing keys first
	keyringDelete(tokenKeyService, keyringUser)
	keyringDelete(secretsKeyService, keyringUser)
	keyringDelete(serviceKeyService, keyringUser)

	// Test successful initialization
	err := InitAuthSystem()
	assert.NoError(t, err)

	// Verify SERVICE_KEY was set
	serviceKey := os.Getenv("SERVICE_KEY")
	assert.NotEmpty(t, serviceKey)

	// Test that subsequent calls work (keys already exist)
	err = InitAuthSystem()
	assert.NoError(t, err)

	// Clean up
	keyringDelete(tokenKeyService, keyringUser)
	keyringDelete(secretsKeyService, keyringUser)
	keyringDelete(serviceKeyService, keyringUser)
	os.Unsetenv("SERVICE_KEY")
}

func TestGenerateTokenErrors(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	// Clean up and initialize
	keyringDelete(tokenKeyService, keyringUser)
	err := InitAuthSystem()
	require.NoError(t, err)

	// Test successful token generation
	user := models.User{
		UUID:  "test-user-123",
		Email: "test@example.com",
	}

	token, err := GenerateToken(user)
	assert.NoError(t, err)
	assert.NotEmpty(t, token)

	// Verify token contents
	valid, parsedToken, err := ValidateToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)

	userID, err := parsedToken.GetString("user-id")
	assert.NoError(t, err)
	assert.Equal(t, user.UUID, userID)

	// Clean up
	keyringDelete(tokenKeyService, keyringUser)
}

func TestGenerateNVMSTokenErrors(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	// Initialize auth system
	err := InitAuthSystem()
	require.NoError(t, err)

	// Test successful NVMS token generation
	project := models.Project{
		UUID: "test-project-456",
		User: models.User{
			UUID: "test-user-789",
		},
	}

	token, err := GenerateNVMSToken(project)
	assert.NoError(t, err)
	assert.NotEmpty(t, token)

	// Verify token contents
	valid, parsedToken, err := ValidateServiceToken(token)
	assert.NoError(t, err)
	assert.True(t, valid)

	userID, err := parsedToken.GetString("user-id")
	assert.NoError(t, err)
	assert.Equal(t, project.User.UUID, userID)

	projectID, err := parsedToken.GetString("project-id")
	assert.NoError(t, err)
	assert.Equal(t, project.UUID, projectID)

	// Clean up
	keyringDelete(serviceKeyService, keyringUser)
}

func TestAuthMiddlewareAdditionalErrors(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Test middleware with missing auth token cookie
	router := gin.New()
	router.Use(AuthMiddleware())
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	// Test request without token cookie
	w := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/protected", nil)
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
	assert.Contains(t, w.Body.String(), "Authorization header missing")

	// Test with invalid token
	w = httptest.NewRecorder()
	req = httptest.NewRequest("GET", "/protected", nil)
	req.AddCookie(&http.Cookie{
		Name:  "authToken",
		Value: "invalid-token",
	})
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
	assert.Contains(t, w.Body.String(), "Invalid or expired token")

	// Test with token that has no user-id claim
	// This is harder to test without mocking the token parsing
}

func TestValidateTokenErrors(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	// Clean up and initialize
	keyringDelete(tokenKeyService, keyringUser)
	err := InitAuthSystem()
	require.NoError(t, err)

	// Test with invalid token format
	valid, token, err := ValidateToken("invalid-token")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, token)

	// Test with empty token
	valid, token, err = ValidateToken("")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, token)

	// Clean up
	keyringDelete(tokenKeyService, keyringUser)
}

func TestValidateServiceTokenErrors(t *testing.T) {
	cleanup := withMockKeyring(t)
	defer cleanup()
	resetServiceEnv()

	// Clean up and initialize
	keyringDelete(serviceKeyService, keyringUser)
	err := InitAuthSystem()
	require.NoError(t, err)

	// Test with invalid service token format
	valid, token, err := ValidateServiceToken("invalid-service-token")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, token)

	// Test with empty service token
	valid, token, err = ValidateServiceToken("")
	assert.Error(t, err)
	assert.False(t, valid)
	assert.Nil(t, token)

	// Test with regular user token (should fail audience validation)
	user := models.User{UUID: "test-user", Email: "test@example.com"}
	userToken, err := GenerateToken(user)
	require.NoError(t, err)

	valid, token, err = ValidateServiceToken(userToken)
	assert.Error(t, err) // Should fail audience check
	assert.False(t, valid)
	assert.Nil(t, token)

	// Clean up
	keyringDelete(serviceKeyService, keyringUser)
	keyringDelete(tokenKeyService, keyringUser)
}
