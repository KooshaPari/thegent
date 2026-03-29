package lib

import (
	"fmt"
	"os"
)

type mockKeyring struct {
	store map[string]map[string]string
}

func newMockKeyring() *mockKeyring {
	return &mockKeyring{store: make(map[string]map[string]string)}
}

func (m *mockKeyring) get(service, user string) (string, error) {
	if users, ok := m.store[service]; ok {
		if val, ok := users[user]; ok {
			return val, nil
		}
	}
	return "", fmt.Errorf("secret not found")
}

func (m *mockKeyring) set(service, user, value string) error {
	if _, ok := m.store[service]; !ok {
		m.store[service] = make(map[string]string)
	}
	m.store[service][user] = value
	return nil
}

func (m *mockKeyring) delete(service, user string) error {
	if users, ok := m.store[service]; ok {
		delete(users, user)
	}
	return nil
}

func withMockKeyring(t cleanupT) func() {
	mock := newMockKeyring()
	originalGet, originalSet, originalDelete := keyringGet, keyringSet, keyringDelete
	keyringGet = mock.get
	keyringSet = mock.set
	keyringDelete = mock.delete
	return func() {
		keyringGet, keyringSet, keyringDelete = originalGet, originalSet, originalDelete
	}
}

type cleanupT interface {
	Helper()
}

func resetServiceEnv() {
	_ = os.Unsetenv("SERVICE_KEY")
}
