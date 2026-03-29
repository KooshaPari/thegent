package bridge

import "time"

type Capability string

const (
	CapabilityChatCompletion Capability = "chat_completion"
	CapabilityEmbeddings     Capability = "embeddings"
	CapabilityRerank         Capability = "rerank"
	CapabilityToolExecution  Capability = "tool_execution"
)

type LaneID string

const (
	LaneLiteLLMDonut LaneID = "litellm_donut"
	LaneBifrost      LaneID = "bifrost"
	LaneNative       LaneID = "native"
)

type EventType string

const (
	EventChunk      EventType = "chunk"
	EventToolCall   EventType = "tool_call"
	EventToolResult EventType = "tool_result"
	EventRouteChange EventType = "route_change"
	EventError      EventType = "error"
	EventDone       EventType = "done"
)

type ExecutionRequest struct {
	BridgeSchemaVersion string                 `json:"bridge_schema_version"`
	RequestID           string                 `json:"request_id"`
	RunID               string                 `json:"run_id"`
	SessionID           string                 `json:"session_id,omitempty"`
	HarnessProfile      string                 `json:"harness_profile"`
	MetaproviderID      string                 `json:"metaprovider_id"`
	LaneID              LaneID                 `json:"lane_id"`
	Intent              Intent                 `json:"intent"`
	ProviderIntent      ProviderIntent         `json:"provider_intent"`
	Governance          GovernancePolicy       `json:"governance"`
	Inputs              ExecutionInputs        `json:"inputs"`
	Context             map[string]any         `json:"context,omitempty"`
	Stream              bool                   `json:"stream"`
	MetaproviderMeta    *MetaproviderMeta      `json:"metaprovider_meta,omitempty"`
	Extra               map[string]any         `json:"extra,omitempty"`
}

type Intent struct {
	Capability  Capability `json:"capability"`
	TaskType    string     `json:"task_type"`
	LatencyTier string     `json:"latency_tier"`
	QualityTier string     `json:"quality_tier"`
}

type ProviderIntent struct {
	ClassOrder  []string `json:"class_order"`
	AllowModels []string `json:"allow_models"`
	DenyModels  []string `json:"deny_models"`
}

type GovernancePolicy struct {
	BudgetUSDMax float64 `json:"budget_usd_max"`
	MaxFallbacks int     `json:"max_fallbacks"`
	RetryPolicy  string  `json:"retry_policy,omitempty"`
	RatePolicyID string  `json:"rate_policy_id,omitempty"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ToolDef struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Schema      map[string]any `json:"schema"`
}

type ExecutionInputs struct {
	Messages   []Message `json:"messages"`
	Tools      []ToolDef `json:"tools"`
	ToolChoice string    `json:"tool_choice"`
}

type MetaproviderMeta struct {
	InheritanceLevel string `json:"inheritance_level"`
	ParentRequestID  string `json:"parent_request_id"`
}

type ExecutionResponse struct {
	BridgeSchemaVersion string            `json:"bridge_schema_version"`
	RequestID           string            `json:"request_id"`
	RunID               string            `json:"run_id"`
	Status              string            `json:"status"`
	SelectedRoute       SelectedRoute     `json:"selected_route"`
	Attempts            int               `json:"attempts"`
	Usage               Usage             `json:"usage"`
	Output              map[string]any    `json:"output"`
	Error               *ResponseError    `json:"error,omitempty"`
	GovernanceOutcome   GovernanceOutcome `json:"governance_outcome"`
}

type SelectedRoute struct {
	ProviderID    string `json:"provider_id"`
	SubproviderID string `json:"subprovider_id"`
	Model         string `json:"model"`
}

type Usage struct {
	InputTokens      int     `json:"input_tokens"`
	OutputTokens     int     `json:"output_tokens"`
	EstimatedCostUSD float64 `json:"estimated_cost_usd"`
}

type ResponseError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Class   string `json:"class"`
}

type GovernanceOutcome struct {
	BudgetCheck    string `json:"budget_check"`
	RateLimitCheck string `json:"rate_limit_check"`
	FallbackUsed   bool   `json:"fallback_used"`
	FallbackDepth  int    `json:"fallback_depth,omitempty"`
}

type ExecutionEvent struct {
	EventType  EventType      `json:"event_type"`
	RequestID  string         `json:"request_id"`
	RunID      string         `json:"run_id"`
	AttemptID  string         `json:"attempt_id"`
	RouteID    string         `json:"route_id,omitempty"`
	ToolCallID string         `json:"tool_call_id,omitempty"`
	TS         time.Time      `json:"ts"`
	Payload    map[string]any `json:"payload"`
}

type RouteCandidate struct {
	RouteID       string           `json:"route_id"`
	ProviderID    string           `json:"provider_id"`
	SubproviderID string           `json:"subprovider_id"`
	ProviderClass string           `json:"provider_class"`
	Model         string           `json:"model"`
	Priority      int              `json:"priority"`
	Constraints   RouteConstraints `json:"constraints"`
}

type RouteConstraints struct {
	RequiresRegion      string  `json:"requires_region,omitempty"`
	MaxCostPer1KTokens  float64 `json:"max_cost_per_1k_tokens,omitempty"`
	SupportsTools       bool    `json:"supports_tools"`
	SupportsStream      bool    `json:"supports_stream"`
}

type HarnessProfile struct {
	HarnessProfile string                `json:"harness_profile"`
	Defaults       HarnessDefaults       `json:"defaults"`
	PolicyOverrides HarnessPolicyOverrides `json:"policy_overrides"`
	ToolPolicy     HarnessToolPolicy     `json:"tool_policy"`
}

type HarnessDefaults struct {
	IntentCapability Capability `json:"intent_capability"`
	LatencyTier      string     `json:"latency_tier"`
	QualityTier      string     `json:"quality_tier"`
}

type HarnessPolicyOverrides struct {
	MaxFallbacks int     `json:"max_fallbacks"`
	BudgetUSDMax float64 `json:"budget_usd_max"`
}

type HarnessToolPolicy struct {
	AllowedToolSets         []string `json:"allowed_tool_sets"`
	RequiresConfirmationFor []string `json:"requires_confirmation_for"`
}

type EventSink interface {
	Emit(event ExecutionEvent) error
}

type ProviderAdapter interface {
	Execute(req ExecutionRequest) (ExecutionResponse, error)
	Stream(req ExecutionRequest, sink EventSink) error
	Capabilities() map[string]any
}

type MetaproviderAdapter interface {
	ProviderAdapter
	ResolveSubproviders(req ExecutionRequest) ([]RouteCandidate, error)
}

type Handler interface {
	Handle(req ExecutionRequest) (ExecutionResponse, error)
}

type Middleware interface {
	Name() string
	Handle(req ExecutionRequest, next Handler) (ExecutionResponse, error)
}

type Runtime interface {
	Register(providerID string, adapter MetaproviderAdapter) error
	Execute(req ExecutionRequest) (ExecutionResponse, error)
	Stream(req ExecutionRequest, sink EventSink) error
}

