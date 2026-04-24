// Package cloud — Local Docker/Podman provider implementation.
// wraps: github.com/moby/moby/v2 (Docker API)
package cloud

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/user"
	"path/filepath"
	"strings"
	"time"

	cerrdefs "github.com/containerd/errdefs"
	"github.com/moby/moby/api/types/container"
	"github.com/moby/moby/api/types/mount"
	"github.com/moby/moby/api/types/network"
	"github.com/moby/moby/client"
)

// LocalProvider implements CloudProvider for local Docker/Podman deployments.
// Credentials.Data may contain:
//   - "socket_path" (optional) — explicit path to Docker/Podman socket
//   - "host" (optional) — Docker daemon host (e.g., "unix:///var/run/docker.sock" or "tcp://localhost:2375")
//
// If neither is provided, the provider auto-detects:
//   1. Docker default: /var/run/docker.sock
//   2. Podman default: /run/user/$UID/podman/podman.sock
//   3. OrbStack: ~/.orbstack/run/docker.sock
//   4. Lima: ~/.lima/default/sock/docker.sock
//   5. Standard DOCKER_HOST env var
type LocalProvider struct {
	credentials Credentials
	metadata    ProviderMetadata
	client      *client.Client
	socketPath  string
	host        string
}

// compile-time interface assertion
var _ CloudProvider = (*LocalProvider)(nil)

// NewLocalProvider constructs a LocalProvider from the supplied credentials.
// Auto-detects Docker/Podman socket if not explicitly provided.
func NewLocalProvider(credentials Credentials) (CloudProvider, error) {
	socketPath := credentials.Data["socket_path"]
	host := credentials.Data["host"]

	// If no explicit config, auto-detect
	if socketPath == "" && host == "" {
		var err error
		host, socketPath, err = autoDetectSocket()
		if err != nil {
			return nil, fmt.Errorf("local: auto-detect socket failed: %w", err)
		}
	}

	// If only socket_path provided, construct host URL
	if host == "" && socketPath != "" {
		host = "unix://" + socketPath
	}

	// Create Docker client
	opts := []client.Opt{
		client.WithHost(host),
		client.WithAPIVersionNegotiation(),
	}
	dc, err := client.NewClientWithOpts(opts...)
	if err != nil {
		return nil, fmt.Errorf("local: failed to create docker client: %w", err)
	}

	return &LocalProvider{
		credentials: credentials,
		socketPath:  socketPath,
		host:        host,
		client:      dc,
		metadata: ProviderMetadata{
			Name:    "local",
			Version: "1.0.0",
			SupportedResources: []ResourceType{
				ResourceTypeComputeContainer,
			},
			Capabilities: []Capability{
				CapabilityLoggable,
				CapabilityExecutable,
			},
			Regions: []Region{
				{ID: "localhost", Name: "Local Machine", Location: "Localhost", Available: true},
			},
			AuthTypes:   []string{"implicit"},
			Description: "Local Docker/Podman container runtime",
		},
	}, nil
}

// GetMetadata returns provider metadata.
func (p *LocalProvider) GetMetadata() ProviderMetadata { return p.metadata }

// SupportsResource returns true only for compute.container.
func (p *LocalProvider) SupportsResource(resourceType ResourceType) bool {
	return resourceType == ResourceTypeComputeContainer
}

// GetCapabilities returns supported capability list.
func (p *LocalProvider) GetCapabilities() []Capability { return p.metadata.Capabilities }

// Initialize validates Docker/Podman connectivity by pinging the daemon.
func (p *LocalProvider) Initialize(ctx context.Context, credentials Credentials) error {
	p.credentials = credentials
	return p.ValidateCredentials(ctx)
}

// ValidateCredentials checks connectivity to the Docker/Podman daemon.
func (p *LocalProvider) ValidateCredentials(ctx context.Context) error {
	_, err := p.client.Ping(ctx, client.PingOptions{})
	if err != nil {
		return fmt.Errorf("local: docker daemon ping failed: %w", err)
	}
	return nil
}

// CreateResource creates a container resource (not yet started).
// config.Spec may contain:
//   - "image" (required) — Docker image name/tag
//   - "cpu_limit" (optional) — CPU limit in CPUs (e.g., 0.5, 1)
//   - "memory_limit" (optional) — Memory limit in MB
//   - "environment" (optional) — map[string]string of env vars
//   - "ports" (optional) — map[string]string of "container_port": "host_port"
func (p *LocalProvider) CreateResource(ctx context.Context, config ResourceConfig) (*Resource, error) {
	if !p.SupportsResource(config.Type) {
		return nil, NewNotSupportedError("local", string(config.Type))
	}

	imageName, ok := config.Spec["image"].(string)
	if !ok || imageName == "" {
		return nil, NewValidationError("local", "image", "Spec.image is required and must be a string")
	}

	now := time.Now()
	res := &Resource{
		ID:           config.Name, // Use container name as resource ID
		Name:         config.Name,
		Type:         ResourceTypeComputeContainer,
		Provider:     "local",
		Region:       "localhost",
		Status:       DeploymentStateProvisioning,
		HealthStatus: HealthStatusUnknown,
		Tags:         config.Tags,
		Metadata: map[string]any{
			"image": imageName,
		},
		CreatedAt: now,
		UpdatedAt: now,
	}

	return res, nil
}

// GetResource retrieves container information by ID (name).
func (p *LocalProvider) GetResource(ctx context.Context, id string) (*Resource, error) {
	result, err := p.client.ContainerInspect(ctx, id, client.ContainerInspectOptions{})
	if err != nil {
		if cerrdefs.IsNotFound(err) {
			return nil, NewResourceNotFoundError("local", id)
		}
		return nil, fmt.Errorf("local: inspect container failed: %w", err)
	}

	return p.containerToResource(result.Container), nil
}

// UpdateResource modifies a container configuration (not supported while running).
func (p *LocalProvider) UpdateResource(ctx context.Context, id string, config ResourceConfig) (*Resource, error) {
	return nil, NewNotSupportedError("local", "UpdateResource — stop container, remove, and create new")
}

// DeleteResource removes a container and all associated data.
func (p *LocalProvider) DeleteResource(ctx context.Context, id string) error {
	// Stop if running
	_, _ = p.client.ContainerStop(ctx, id, client.ContainerStopOptions{})
	// Remove
	if _, err := p.client.ContainerRemove(ctx, id, client.ContainerRemoveOptions{Force: true}); err != nil {
		if cerrdefs.IsNotFound(err) {
			return nil // Already gone
		}
		return fmt.Errorf("local: remove container failed: %w", err)
	}
	return nil
}

// ListResources returns containers matching the filter.
func (p *LocalProvider) ListResources(ctx context.Context, filter ResourceFilter) ([]*Resource, error) {
	result, err := p.client.ContainerList(ctx, client.ContainerListOptions{All: true})
	if err != nil {
		return nil, fmt.Errorf("local: list containers failed: %w", err)
	}

	resources := make([]*Resource, 0, len(result.Items))
	for _, c := range result.Items {
		res := &Resource{
			ID:       c.ID[:12], // Short ID
			Name:     strings.TrimPrefix(c.Names[0], "/"),
			Type:     ResourceTypeComputeContainer,
			Provider: "local",
			Region:   "localhost",
			Status:   p.dockerStateToDeploymentState(string(c.State)),
			Tags:     c.Labels,
			Metadata: map[string]any{
				"image":      c.Image,
				"full_id":    c.ID,
				"created_at": time.Unix(c.Created, 0),
			},
			CreatedAt: time.Unix(c.Created, 0),
			UpdatedAt: time.Now(),
		}

		// Add port endpoints. c.Ports is []container.Port from the list API,
		// where each entry carries its own IP/PrivatePort/PublicPort/Type.
		for _, port := range c.Ports {
			if port.PublicPort == 0 {
				continue
			}
			res.Endpoints = append(res.Endpoints, Endpoint{
				Type:     port.Type,
				URL:      fmt.Sprintf("localhost:%d", port.PublicPort),
				Port:     int(port.PrivatePort),
				Protocol: port.Type,
				Primary:  len(res.Endpoints) == 0,
			})
		}

		resources = append(resources, res)
	}

	return resources, nil
}

// Deploy starts a container based on DeploymentConfig.
// config.Source.Type can be "docker" (image name) or "git" (not supported yet).
// config.Env and config.Secrets are merged into container environment.
// config.Config may contain:
//   - "image" (required) — Docker image
//   - "cpu_limit" (optional) — CPU limit in CPUs
//   - "memory_limit" (optional) — Memory limit in MB
//   - "environment" (optional) — map of env vars
//   - "ports" (optional) — map of "container_port": "host_port"
//   - "volumes" (optional) — map of "/container/path": "/host/path"
func (p *LocalProvider) Deploy(ctx context.Context, deployment DeploymentConfig) (*Deployment, error) {
	if deployment.ResourceID == "" {
		return nil, NewValidationError("local", "resource_id", "ResourceID is required")
	}

	// Determine image
	imageName := ""
	if deployment.Source != nil {
		imageName = deployment.Source.Image
	}
	if imageName == "" {
		if img, ok := deployment.Config["image"].(string); ok {
			imageName = img
		}
	}
	if imageName == "" {
		return nil, NewValidationError("local", "image", "Image must be specified in Source or Config")
	}

	now := time.Now()

	// Pull image if needed (simple best-effort)
	_ = p.pullImage(ctx, imageName)

	// Build environment
	env := make([]string, 0)
	for k, v := range deployment.Env {
		env = append(env, fmt.Sprintf("%s=%s", k, v))
	}
	for k, v := range deployment.Secrets {
		env = append(env, fmt.Sprintf("%s=%s", k, v))
	}

	// Create Resources (CPU/Memory limits)
	res := &container.Resources{}

	// Parse CPU limit (in CPUs, convert to nanoseconds)
	if cpu, ok := deployment.Config["cpu_limit"].(float64); ok && cpu > 0 {
		res.NanoCPUs = int64(cpu * 1e9)
	}

	// Parse memory limit (in MB, convert to bytes)
	if mem, ok := deployment.Config["memory_limit"].(float64); ok && mem > 0 {
		res.Memory = int64(mem * 1024 * 1024)
	}

	// Create host config
	hostCfg := &container.HostConfig{
		Resources: *res,
	}

	// Parse ports
	if ports, ok := deployment.Config["ports"].(map[string]interface{}); ok {
		portBindings := make(network.PortMap)
		for containerPort, hostPort := range ports {
			p, err := network.ParsePort(containerPort)
			if err != nil {
				return nil, NewValidationError("local", "ports", fmt.Sprintf("invalid container port %q: %v", containerPort, err))
			}
			portBindings[p] = []network.PortBinding{
				{HostPort: fmt.Sprint(hostPort)},
			}
		}
		hostCfg.PortBindings = portBindings
	}

	// Parse volumes
	if volumes, ok := deployment.Config["volumes"].(map[string]interface{}); ok {
		mounts := make([]mount.Mount, 0)
		for containerPath, hostPath := range volumes {
			mounts = append(mounts, mount.Mount{
				Type:   mount.TypeBind,
				Source: fmt.Sprint(hostPath),
				Target: containerPath,
			})
		}
		hostCfg.Mounts = mounts
	}

	// Create container
	containerCfg := &container.Config{
		Image: imageName,
		Env:   env,
	}

	resp, err := p.client.ContainerCreate(ctx, client.ContainerCreateOptions{
		Config:     containerCfg,
		HostConfig: hostCfg,
		Name:       deployment.ResourceID,
	})
	if err != nil {
		return nil, NewProvisioningError("local", "creating", fmt.Sprintf("failed to create container: %v", err), err)
	}

	// Start container
	if _, err := p.client.ContainerStart(ctx, resp.ID, client.ContainerStartOptions{}); err != nil {
		_, _ = p.client.ContainerRemove(ctx, resp.ID, client.ContainerRemoveOptions{Force: true})
		return nil, NewProvisioningError("local", "starting", fmt.Sprintf("failed to start container: %v", err), err)
	}

	return &Deployment{
		ID:         resp.ID[:12],
		ResourceID: deployment.ResourceID,
		Version:    deployment.Version,
		State:      DeploymentStateActive,
		Strategy:   deployment.Strategy,
		Progress:   100,
		Message:    "Container started successfully",
		StartedAt:  now,
		UpdatedAt:  now,
	}, nil
}

// GetDeploymentStatus retrieves the current status of a deployment (container).
func (p *LocalProvider) GetDeploymentStatus(ctx context.Context, id string) (*DeploymentStatus, error) {
	result, err := p.client.ContainerInspect(ctx, id, client.ContainerInspectOptions{})
	if err != nil {
		if cerrdefs.IsNotFound(err) {
			return nil, NewResourceNotFoundError("local", id)
		}
		return nil, fmt.Errorf("local: inspect container failed: %w", err)
	}

	containerInfo := result.Container
	var stateStatus container.ContainerState
	var stateStartedAt string
	var stateHealth *container.Health
	if containerInfo.State != nil {
		stateStatus = containerInfo.State.Status
		stateStartedAt = containerInfo.State.StartedAt
		stateHealth = containerInfo.State.Health
	}
	state := p.dockerStateToDeploymentState(string(stateStatus))
	health := p.dockerStateToHealth(string(stateStatus), stateHealth)

	// Parse StartedAt timestamp
	startedAt := time.Now()
	if stateStartedAt != "" {
		if t, err := time.Parse(time.RFC3339Nano, stateStartedAt); err == nil {
			startedAt = t
		}
	}

	instances := []InstanceInfo{
		{
			ID:        containerInfo.ID[:12],
			State:     string(stateStatus),
			Health:    health,
			Region:    "localhost",
			StartedAt: startedAt,
		},
	}

	return &DeploymentStatus{
		Deployment: &Deployment{
			ID:         containerInfo.ID[:12],
			ResourceID: strings.TrimPrefix(containerInfo.Name, "/"),
			State:      state,
			StartedAt:  startedAt,
			UpdatedAt:  time.Now(),
		},
		Health:    health,
		Instances: instances,
	}, nil
}

// RollbackDeployment is not supported (containers are immutable).
func (p *LocalProvider) RollbackDeployment(ctx context.Context, id string) error {
	return NewNotSupportedError("local", "RollbackDeployment — remove and redeploy container")
}

// GetLogs retrieves logs from a container.
func (p *LocalProvider) GetLogs(ctx context.Context, resource *Resource, opts LogOptions) (LogStream, error) {
	readCloser, err := p.client.ContainerLogs(ctx, resource.ID, client.ContainerLogsOptions{
		ShowStdout: true,
		ShowStderr: true,
		Follow:     opts.Follow,
		Tail:       fmt.Sprint(opts.Tail),
	})
	if err != nil {
		return nil, fmt.Errorf("local: get logs failed: %w", err)
	}

	return &localLogStream{reader: readCloser}, nil
}

// GetMetrics retrieves resource usage metrics from a container.
func (p *LocalProvider) GetMetrics(ctx context.Context, resource *Resource, opts MetricOptions) ([]Metric, error) {
	stats, err := p.client.ContainerStats(ctx, resource.ID, client.ContainerStatsOptions{Stream: false})
	if err != nil {
		return nil, fmt.Errorf("local: get stats failed: %w", err)
	}
	defer stats.Body.Close()

	var statsJSON struct {
		CPUStats struct {
			CPUUsage struct {
				TotalUsage        uint64 `json:"total_usage"`
				SystemCPUUsage    uint64 `json:"system_cpu_usage"`
				UsageInKernelmode uint64 `json:"usage_in_kernelmode"`
				UsageInUsermode   uint64 `json:"usage_in_usermode"`
			} `json:"cpu_usage"`
			SystemCPUUsage uint64 `json:"system_cpu_usage"`
		} `json:"cpu_stats"`
		MemoryStats struct {
			Usage    uint64 `json:"usage"`
			MaxUsage uint64 `json:"max_usage"`
			Limit    uint64 `json:"limit"`
		} `json:"memory_stats"`
	}

	if err := json.NewDecoder(stats.Body).Decode(&statsJSON); err != nil {
		return nil, fmt.Errorf("local: decode stats failed: %w", err)
	}

	now := time.Now()
	metrics := []Metric{}

	// CPU percentage calculation: (CPU delta / system delta) * cores * 100
	if statsJSON.CPUStats.SystemCPUUsage > 0 {
		cpuDelta := float64(statsJSON.CPUStats.CPUUsage.TotalUsage)
		systemDelta := float64(statsJSON.CPUStats.SystemCPUUsage)
		cpuPercent := (cpuDelta / systemDelta) * 100.0
		metrics = append(metrics, Metric{
			Name:      "cpu_percent",
			Value:     cpuPercent,
			Unit:      "percent",
			Timestamp: now,
		})
	}

	// Memory usage in bytes
	metrics = append(metrics, Metric{
		Name:      "memory_bytes",
		Value:     float64(statsJSON.MemoryStats.Usage),
		Unit:      "bytes",
		Timestamp: now,
	})

	// Memory percent (if limit is set)
	if statsJSON.MemoryStats.Limit > 0 {
		memPercent := (float64(statsJSON.MemoryStats.Usage) / float64(statsJSON.MemoryStats.Limit)) * 100.0
		metrics = append(metrics, Metric{
			Name:      "memory_percent",
			Value:     memPercent,
			Unit:      "percent",
			Timestamp: now,
		})
	}

	return metrics, nil
}

// EstimateCost returns zero-cost estimate (local containers are free).
func (p *LocalProvider) EstimateCost(ctx context.Context, config ResourceConfig) (*CostEstimate, error) {
	return &CostEstimate{
		HourlyUSD:   0,
		DailyUSD:    0,
		MonthlyUSD:  0,
		Breakdown:   map[string]float64{"compute": 0},
		Confidence:  "high",
		Currency:    "USD",
		LastUpdated: time.Now(),
	}, nil
}

// GetActualCost returns zero-cost (local containers are free).
func (p *LocalProvider) GetActualCost(ctx context.Context, resource *Resource, timeRange TimeRange) (*Cost, error) {
	return &Cost{
		TotalUSD:  0,
		Breakdown: map[string]float64{"compute": 0},
		StartTime: timeRange.Start,
		EndTime:   timeRange.End,
		Currency:  "USD",
	}, nil
}

// ---------------------------------------------------------------------------
// Helper functions
// ---------------------------------------------------------------------------

// autoDetectSocket attempts to find a Docker/Podman socket on the system.
func autoDetectSocket() (string, string, error) {
	candidates := []string{
		"/var/run/docker.sock",                          // Docker default
	}

	// Add Podman user socket
	if u, err := user.Current(); err == nil {
		candidates = append(candidates, fmt.Sprintf("/run/user/%s/podman/podman.sock", u.Uid))
	}

	// Add OrbStack
	if home, err := os.UserHomeDir(); err == nil {
		candidates = append(candidates,
			filepath.Join(home, ".orbstack/run/docker.sock"),
			filepath.Join(home, ".lima/default/sock/docker.sock"),
		)
	}

	// Check environment variable
	if envHost := os.Getenv("DOCKER_HOST"); envHost != "" {
		return envHost, "", nil
	}

	// Try candidates
	for _, sock := range candidates {
		if info, err := os.Stat(sock); err == nil && !info.IsDir() {
			return "unix://" + sock, sock, nil
		}
	}

	return "", "", fmt.Errorf("no docker/podman socket found (tried: %v)", candidates)
}

// pullImage attempts to pull an image from the registry (best-effort).
func (p *LocalProvider) pullImage(ctx context.Context, imageName string) error {
	_, err := p.client.ImagePull(ctx, imageName, client.ImagePullOptions{})
	if err == nil || strings.Contains(err.Error(), "already exists") {
		return nil
	}
	// Ignore pull errors; image may already exist locally
	return nil
}

// containerToResource converts a Docker container to a Resource.
func (p *LocalProvider) containerToResource(c container.InspectResponse) *Resource {
	var stateStatus container.ContainerState
	var stateHealth *container.Health
	var stateExitCode int
	if c.State != nil {
		stateStatus = c.State.Status
		stateHealth = c.State.Health
		stateExitCode = c.State.ExitCode
	}
	state := p.dockerStateToDeploymentState(string(stateStatus))

	// Parse timestamps
	createdAt := time.Now()
	if c.Created != "" {
		if t, err := time.Parse(time.RFC3339Nano, c.Created); err == nil {
			createdAt = t
		}
	}

	var (
		image  string
		labels map[string]string
	)
	if c.Config != nil {
		image = c.Config.Image
		labels = c.Config.Labels
	}

	res := &Resource{
		ID:           c.ID[:12],
		Name:         strings.TrimPrefix(c.Name, "/"),
		Type:         ResourceTypeComputeContainer,
		Provider:     "local",
		Region:       "localhost",
		Status:       state,
		HealthStatus: p.dockerStateToHealth(string(stateStatus), stateHealth),
		Tags:         labels,
		Metadata: map[string]any{
			"image":     image,
			"full_id":   c.ID,
			"exit_code": stateExitCode,
		},
		CreatedAt: createdAt,
		UpdatedAt: time.Now(),
	}

	// Add endpoints for exposed ports
	if c.NetworkSettings != nil {
		for port, bindings := range c.NetworkSettings.Ports {
			if len(bindings) > 0 {
				proto := string(port.Proto())
				res.Endpoints = append(res.Endpoints, Endpoint{
					Type:     proto,
					URL:      fmt.Sprintf("localhost:%s", bindings[0].HostPort),
					Port:     int(port.Num()),
					Protocol: proto,
					Primary:  len(res.Endpoints) == 0,
				})
			}
		}
	}

	return res
}

// dockerStateToDeploymentState maps Docker container state to DeploymentState.
func (p *LocalProvider) dockerStateToDeploymentState(state string) DeploymentState {
	switch state {
	case "created":
		return DeploymentStateProvisioning
	case "running":
		return DeploymentStateActive
	case "paused":
		return DeploymentStateDegraded
	case "restarting":
		return DeploymentStateUpdating
	case "removing":
		return DeploymentStateDeleting
	case "exited", "dead":
		return DeploymentStateDeleted
	default:
		return DeploymentStateProvisioning
	}
}

// dockerStateToHealth maps Docker container state to HealthStatus.
func (p *LocalProvider) dockerStateToHealth(state string, health *container.Health) HealthStatus {
	if health != nil {
		switch string(health.Status) {
		case "healthy":
			return HealthStatusHealthy
		case "unhealthy":
			return HealthStatusUnhealthy
		case "starting":
			return HealthStatusChecking
		}
	}

	switch state {
	case "running":
		return HealthStatusHealthy
	case "paused":
		return HealthStatusDegraded
	case "exited", "dead":
		return HealthStatusUnhealthy
	default:
		return HealthStatusUnknown
	}
}

// ---------------------------------------------------------------------------
// LogStream implementation for local containers
// ---------------------------------------------------------------------------

type localLogStream struct {
	reader io.ReadCloser
	// Docker logs use a multiplexing protocol; parse as plaintext for simplicity
	scanner *bufio.Scanner
	eof     bool
}

func (s *localLogStream) Next() (*LogEntry, error) {
	if s.scanner == nil {
		s.scanner = bufio.NewScanner(s.reader)
	}

	if !s.scanner.Scan() {
		s.eof = true
		if err := s.scanner.Err(); err != nil {
			return nil, err
		}
		return nil, io.EOF
	}

	line := s.scanner.Bytes()

	// Docker daemon may include a 8-byte header per line (multiplexing). Try to skip it.
	if len(line) > 8 {
		// Header format: [stream_type][0][0][0][size:4 bytes]
		// For simplicity, just use the data as-is.
		line = line[8:]
	}

	return &LogEntry{
		Timestamp: time.Now(),
		Message:   string(line),
	}, nil
}

func (s *localLogStream) Close() error {
	return s.reader.Close()
}

// ---------------------------------------------------------------------------
// Registry init
// ---------------------------------------------------------------------------

func init() {
	MustRegister(
		ProviderMetadata{
			Name:    "local",
			Version: "1.0.0",
			SupportedResources: []ResourceType{
				ResourceTypeComputeContainer,
			},
			Capabilities: []Capability{
				CapabilityLoggable,
				CapabilityExecutable,
			},
			Regions: []Region{
				{ID: "localhost", Name: "Local Machine", Location: "Localhost", Available: true},
			},
			AuthTypes:   []string{"implicit"},
			Description: "Local Docker/Podman container runtime",
		},
		NewLocalProvider,
	)
}
