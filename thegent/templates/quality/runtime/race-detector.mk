# Race Detector — Go data race detection
# The Go race detector instruments memory accesses at compile time
# and detects concurrent access without synchronization at runtime.
#
# Usage: Add -race flag to go test/build/run commands
# Note: Increases build time ~2x and memory usage ~5-10x

# Run all tests with race detector
.PHONY: test-race
test-race:
	go test -race -count=1 ./...

# Run specific package tests with race detection
.PHONY: test-race-pkg
test-race-pkg:
	go test -race -count=1 -v $(PKG)

# Build with race detector (for integration/smoke testing)
.PHONY: build-race
build-race:
	go build -race -o ./bin/$(APP)-race ./cmd/$(APP)

# Run benchmarks with race detector
.PHONY: bench-race
bench-race:
	go test -race -bench=. -benchmem ./...

# CI target: race detection + coverage
.PHONY: ci-race
ci-race:
	go test -race -coverprofile=coverage-race.out -count=1 ./...
