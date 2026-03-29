//go:build examples
// +build examples

package examples

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDummyFunction(t *testing.T) {
	result := DummyFunction()
	assert.Equal(t, "dummy", result)
}
