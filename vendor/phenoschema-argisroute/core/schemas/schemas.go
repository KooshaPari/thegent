package schemas

import (
	"context"
	"sync"
	"time"
)

type Provider string

const (
	ProviderOpenAI    Provider = "openai"
	ProviderAnthropic Provider = "anthropic"
	ProviderGemini    Provider = "gemini"
	ProviderCustom   Provider = "custom"
)

type LogLevel string

const (
	LogLevelDebug LogLevel = "debug"
	LogLevelInfo  LogLevel = "info"
	LogLevelWarn  LogLevel = "warn"
	LogLevelError LogLevel = "error"
)

type Logger interface {
	Debug(msg string, args ...interface{})
	Info(msg string, args ...interface{})
	Warn(msg string, args ...interface{})
	Error(msg string, args ...interface{})
}

// Plugin interface - pointer receivers, correct return types
type Plugin interface {
	GetName() string
	Config() map[string]interface{}
	TransportInterceptor(ctx context.Context, req *BifrostRequest) (*BifrostRequest, *BifrostError, error)
	PreHook(ctx context.Context, req *BifrostRequest) (*BifrostRequest, error)
	PostHook(ctx context.Context, resp *BifrostResponse) (*BifrostResponse, *BifrostError, error)
	Cleanup() error
}

type Account struct {
	ID                string          `json:"id"`
	Name              string          `json:"name"`
	Email             string          `json:"email"`
	Providers         []Provider      `json:"providers"`
	Configs           []ProviderConfig `json:"configs"`
	Keys              []Key           `json:"keys"`
	DefaultProvider   Provider        `json:"default_provider"`
	NetworkConfig     NetworkConfig   `json:"network_config"`
	CreatedAt         time.Time      `json:"created_at"`
	UpdatedAt         time.Time      `json:"updated_at"`
}

func (a *Account) GetConfiguredProviders() []Provider {
	providers := make([]Provider, 0, len(a.Configs))
	seen := make(map[Provider]bool)
	for _, cfg := range a.Configs {
		if !seen[cfg.Provider] {
			providers = append(providers, cfg.Provider)
			seen[cfg.Provider] = true
		}
	}
	return providers
}

func (a *Account) GetConfigForProvider(provider Provider) (*ProviderConfig, bool) {
	for i := range a.Configs {
		if a.Configs[i].Provider == provider {
			return &a.Configs[i], true
		}
	}
	return nil, false
}

func (a *Account) GetConfigForProviderError(provider Provider) (*ProviderConfig, error) {
	for i := range a.Configs {
		if a.Configs[i].Provider == provider {
			return &a.Configs[i], nil
		}
	}
	return nil, &BifrostError{Message: "provider not found", Code: 404}
}

func (a *Account) GetKeysForProvider(_ context.Context, provider Provider) ([]Key, error) {
	keys := make([]Key, 0)
	for _, key := range a.Keys {
		if key.Provider == provider && key.IsActive {
			keys = append(keys, key)
		}
	}
	return keys, nil
}

func (a *Account) SetKeys(keys []Key) {
	a.Keys = keys
}

type ProviderConfig struct {
	Provider               Provider                 `json:"provider"`
	BaseURL                string                  `json:"base_url"`
	APIKey                 string                  `json:"api_key,omitempty"`
	Timeout                time.Duration           `json:"timeout"`
	Headers                map[string]string       `json:"headers"`
	ExtraParams            map[string]interface{}  `json:"extra_params"`
	ConcurrencyAndBuffer   ConcurrencyAndBuffer   `json:"concurrency_and_buffer,omitempty"`
	BufferSize             int                    `json:"buffer_size,omitempty"`
	NetworkConfig          *NetworkConfig         `json:"network_config,omitempty"`
	Dimensions             int                    `json:"dimensions,omitempty"`
}

type Key struct {
	ID         string     `json:"id"`
	Name       string     `json:"name"`
	Provider   Provider   `json:"provider"`
	Value      string     `json:"value,omitempty"`
	IsActive   bool       `json:"is_active"`
	Weight     int        `json:"weight,omitempty"`
	CreatedAt  time.Time `json:"created_at"`
	ExpiresAt  *time.Time `json:"expires_at,omitempty"`
}

type NetworkConfig struct {
	Timeout                      time.Duration `json:"timeout"`
	MaxRetries                  int           `json:"max_retries"`
	RetryBackoff                time.Duration `json:"retry_backoff"`
	MaxIdleConns                 int           `json:"max_idle_conns"`
	IdleConnTimeout              time.Duration `json:"idle_conn_timeout"`
	DefaultRequestTimeoutInSeconds int         `json:"default_request_timeout_in_seconds,omitempty"`
	RetryBackoffInitial          time.Duration `json:"retry_backoff_initial,omitempty"`
	RetryBackoffMax             time.Duration `json:"retry_backoff_max,omitempty"`
}

func (nc *NetworkConfig) GetDefaultRequestTimeoutInSeconds() int {
	if nc.DefaultRequestTimeoutInSeconds > 0 {
		return nc.DefaultRequestTimeoutInSeconds
	}
	if nc.Timeout.Seconds() > 0 {
		return int(nc.Timeout.Seconds())
	}
	return 30
}

func (nc *NetworkConfig) GetRetryBackoffInitial() time.Duration {
	if nc.RetryBackoffInitial > 0 {
		return nc.RetryBackoffInitial
	}
	return nc.RetryBackoff
}

func (nc *NetworkConfig) GetRetryBackoffMax() time.Duration {
	if nc.RetryBackoffMax > 0 {
		return nc.RetryBackoffMax
	}
	return nc.RetryBackoff * 2
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatMessageContent struct {
	Type string `json:"type,omitempty"`
	Text string `json:"text,omitempty"`
}

type CompletionRequest struct {
	Model            string    `json:"model"`
	Messages         []Message `json:"messages"`
	MaxTokens        int       `json:"max_tokens,omitempty"`
	Temperature      float64   `json:"temperature,omitempty"`
	TopP             float64   `json:"top_p,omitempty"`
	FrequencyPenalty float64   `json:"frequency_penalty,omitempty"`
	PresencePenalty  float64   `json:"presence_penalty,omitempty"`
	Input            string    `json:"input,omitempty"`
	Params           *ChatParams `json:"params,omitempty"`
}

type ChatRequest struct {
	Model    string          `json:"model"`
	Messages []ChatMessage   `json:"messages"`
	Params   *ChatParameters `json:"params,omitempty"`
}

type ChatParams struct {
	Tools []ChatTool `json:"tools,omitempty"`
}

type ChatParameters struct {
	Model               string  `json:"model"`
	MaxTokens           int     `json:"max_tokens,omitempty"`
	MaxCompletionTokens int     `json:"max_completion_tokens,omitempty"`
	Temperature         float64 `json:"temperature,omitempty"`
	TopP                float64 `json:"top_p,omitempty"`
	FrequencyPenalty    float64 `json:"frequency_penalty,omitempty"`
	PresencePenalty     float64 `json:"presence_penalty,omitempty"`
}

func (cp ChatParameters) ToCompletionParams() CompletionParams {
	return CompletionParams{
		MaxTokens:   cp.MaxTokens,
		Temperature: cp.Temperature,
		TopP:        cp.TopP,
	}
}

type CompletionParams struct {
	MaxTokens        int     `json:"max_tokens,omitempty"`
	Temperature      float64 `json:"temperature,omitempty"`
	TopP             float64 `json:"top_p,omitempty"`
	FrequencyPenalty float64 `json:"frequency_penalty,omitempty"`
	PresencePenalty  float64 `json:"presence_penalty,omitempty"`
}

type CompletionResponse struct {
	ID      string `json:"id"`
	Content string `json:"content"`
	Model   string `json:"model"`
	Usage   Usage  `json:"usage"`
	Created int64  `json:"created,omitempty"`
	Object  string `json:"object,omitempty"`
}

type Choice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason,omitempty"`
}

type EmbeddingRequest struct {
	Provider Provider   `json:"provider"`
	Model    string     `json:"model"`
	Input    string     `json:"input,omitempty"`
	Texts    []string   `json:"texts,omitempty"`
	Params   *EmbeddingParams `json:"params,omitempty"`
}

type EmbeddingData struct {
	Embedding []float32 `json:"embedding"`
	Index     int       `json:"index"`
	Object    string    `json:"object,omitempty"`
}

type EmbeddingResponse struct {
	Data  []EmbeddingData `json:"data"`
	Model string          `json:"model"`
	Usage Usage           `json:"usage"`
	Object string         `json:"object,omitempty"`
}

type EmbeddingParams struct {
	ExtraParams map[string]interface{} `json:"extra_params,omitempty"`
	Dimensions  int                   `json:"dimensions,omitempty"`
}

type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type BifrostRequest struct {
	CompletionRequest *CompletionRequest  `json:"completion_request,omitempty"`
	EmbeddingRequest  *EmbeddingRequest  `json:"embedding_request,omitempty"`
	ChatRequest       *ChatRequest     `json:"chat_request,omitempty"`
	Params            map[string]interface{} `json:"params,omitempty"`
}

func (r *BifrostRequest) SetModel(model string) {
	if r.ChatRequest != nil {
		r.ChatRequest.Model = model
	}
	if r.CompletionRequest != nil {
		r.CompletionRequest.Model = model
	}
}

func (r *BifrostRequest) SetProvider(provider Provider) {}

func (r *BifrostRequest) TextCompletionRequest() *CompletionRequest {
	return r.CompletionRequest
}

type BifrostResponse struct {
	CompletionResponse *CompletionResponse `json:"completion_response,omitempty"`
	EmbeddingResponse  *EmbeddingResponse  `json:"embedding_response,omitempty"`
	ChatResponse       *ChatResponse     `json:"chat_response,omitempty"`
	ExtraFields        map[string]interface{} `json:"extra_fields,omitempty"`
}

func (r *BifrostResponse) GetModel() string {
	if r.ChatResponse != nil {
		return r.ChatResponse.Model
	}
	if r.CompletionResponse != nil {
		return r.CompletionResponse.Model
	}
	return ""
}

type BifrostError struct {
	Message        string      `json:"message"`
	Code           int         `json:"code"`
	StatusCode     *int        `json:"status_code,omitempty"`
	AllowFallbacks *bool       `json:"allow_fallbacks,omitempty"`
	RawError       error       `json:"-"`
	Err            *ErrorField `json:"err,omitempty"`
}

func (e BifrostError) Error() string {
	return e.Message
}

type ErrorField struct {
	Message string `json:"message"`
	Code    int    `json:"code"`
}

type ChatTool struct {
	Type     string        `json:"type"`
	Function ChatFunction `json:"function,omitempty"`
}

type ChatFunction struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

type ChatResponseChoice struct {
	Index        int         `json:"index"`
	Message      ChatMessage `json:"message"`
	FinishReason string      `json:"finish_reason,omitempty"`
}

type ChatResponse struct {
	ID      string               `json:"id"`
	Object  string               `json:"object"`
	Created int64                `json:"created"`
	Model   string               `json:"model"`
	Choices []ChatResponseChoice `json:"choices"`
	Usage   Usage                `json:"usage,omitempty"`
}

func (r *ChatResponse) Content() string {
	if len(r.Choices) > 0 && r.Choices[0].Message.Content != "" {
		return r.Choices[0].Message.Content
	}
	return ""
}

type ChatMessageRole string

const (
	RoleSystem    ChatMessageRole = "system"
	RoleUser      ChatMessageRole = "user"
	RoleAssistant ChatMessageRole = "assistant"
)

const ChatMessageRoleSystem = ChatMessageRole("system")

type LLMUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type BifrostChatRequest struct {
	Model            string                  `json:"model"`
	Messages         []BifrostChatMessage  `json:"messages"`
	Temperature      *float64                `json:"temperature,omitempty"`
	MaxTokens        *int                   `json:"max_tokens,omitempty"`
	Stream           bool                   `json:"stream,omitempty"`
	TopP             *float64                `json:"top_p,omitempty"`
	FrequencyPenalty *float64                `json:"frequency_penalty,omitempty"`
	PresencePenalty  *float64                `json:"presence_penalty,omitempty"`
}

type BifrostChatMessage struct {
	Role    string               `json:"role"`
	Content BifrostChatContent   `json:"content"`
}

type BifrostChatContent struct {
	Text string `json:"text"`
}

type ChatDelta struct {
	Role    string `json:"role,omitempty"`
	Content string `json:"content,omitempty"`
}

type BifrostResponseChoice struct {
	Index        int          `json:"index"`
	Message      *ChatMessage `json:"message,omitempty"`
	FinishReason string       `json:"finish_reason,omitempty"`
	Text         string       `json:"text,omitempty"`
	Delta        *ChatDelta   `json:"delta,omitempty"`
}

type BifrostNonStreamResponse struct {
	ID      string                    `json:"id"`
	Choices []BifrostResponseChoice `json:"choices,omitempty"`
	Usage   *Usage                   `json:"usage,omitempty"`
	Model   string                    `json:"model,omitempty"`
	Object  string                    `json:"object,omitempty"`
}

type BifrostStreamResponse struct {
	ID                  string               `json:"id"`
	Object              string               `json:"object"`
	Created             int64                `json:"created"`
	Model               string               `json:"model"`
	Choices             []ChatResponseChoice `json:"choices"`
	BifrostError        *BifrostError       `json:"error,omitempty"`
	BifrostChatResponse *ChatResponse        `json:"chat_response,omitempty"`
}

type BifrostStream struct {
	ID      string              `json:"id"`
	Object  string              `json:"object"`
	Created int64               `json:"created"`
	Model   string              `json:"model"`
	Choices []ChatResponseChoice `json:"choices"`
}

func (b BifrostNonStreamResponse) TruncateToFit() {}
func (b BifrostStream) TruncateToFit() {}

type BifrostTextCompletionRequest = CompletionRequest
type BifrostTextCompletionResponse = CompletionResponse

type Content struct {
	Type string `json:"type"`
	Text string `json:"text,omitempty"`
}

type PluginShortCircuit struct {
	Response BifrostResponse
	Error    error
}

type BifrostConfig struct {
	Account         *EnhancedAccount
	Plugins         []Plugin
	LogLevel        LogLevel
	Logger          Logger
	InitialPoolSize int
}

type EnhancedAccount struct {
	Account
	fallback *Account
	mu       sync.RWMutex
}

func NewEnhancedAccount(account *Account) *EnhancedAccount {
	return &EnhancedAccount{
		Account:  *account,
		fallback: nil,
	}
}

func (a *EnhancedAccount) GetFallback() *Account {
	a.mu.RLock()
	defer a.mu.RUnlock()
	return a.fallback
}

func (a *EnhancedAccount) SetFallback(fallback *Account) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.fallback = fallback
}

func (a *EnhancedAccount) DefaultProvider() Provider {
	return a.Account.DefaultProvider
}

func (a *EnhancedAccount) SetDefaultProvider(provider Provider) {
	a.Account.DefaultProvider = provider
}

func (a *EnhancedAccount) WeightedKeys(provider Provider) ([]Key, error) {
	a.mu.RLock()
	defer a.mu.RUnlock()
	keys := make([]Key, 0)
	for _, key := range a.Keys {
		if key.Provider == provider && key.IsActive {
			keys = append(keys, key)
		}
	}
	return keys, nil
}

func (a *EnhancedAccount) SetKeys(provider Provider, keys []Key) {
	if &a.Account != nil {
		newKeys := make([]Key, 0)
		for _, key := range a.Account.Keys {
			if key.Provider != provider {
				newKeys = append(newKeys, key)
			}
		}
		newKeys = append(newKeys, keys...)
		a.Account.Keys = newKeys
	}
}

func (a *EnhancedAccount) SetConfig(provider Provider, config *ProviderConfig) {
	if &a.Account != nil {
		for i := range a.Account.Configs {
			if a.Account.Configs[i].Provider == provider {
				a.Account.Configs[i] = *config
				return
			}
		}
		a.Account.Configs = append(a.Account.Configs, *config)
	}
}

type Model struct {
	ID       string `json:"id"`
	Provider string `json:"provider"`
	Name     string `json:"name"`
	Object   string `json:"object,omitempty"`
	Created  int64  `json:"created,omitempty"`
	OwnedBy  string `json:"owned_by,omitempty"`
}

type ModelProvider = Provider

const (
	Gemini    ModelProvider = "gemini"
	OpenAI    ModelProvider = "openai"
	Anthropic ModelProvider = "anthropic"
)

func NewDefaultLogger(level LogLevel) Logger {
	return &defaultLogger{level: level}
}

type defaultLogger struct {
	level LogLevel
}

func (l *defaultLogger) Debug(msg string, args ...interface{}) {}
func (l *defaultLogger) Info(msg string, args ...interface{}) {}
func (l *defaultLogger) Warn(msg string, args ...interface{}) {}
func (l *defaultLogger) Error(msg string, args ...interface{}) {}

// ConcurrencyAndBuffer struct
type ConcurrencyAndBuffer struct {
	Concurrency int `json:"concurrency"`
	Buffer     int `json:"buffer"`
}

type ConcurrencyAndBufferSize = ConcurrencyAndBuffer

func (c ConcurrencyAndBuffer) GetConcurrency() int { return c.Concurrency }
func (c ConcurrencyAndBuffer) GetBufferSize() int { return c.Buffer }

func NewConcurrencyAndBufferSize(c, b int) ConcurrencyAndBuffer {
	return ConcurrencyAndBuffer{Concurrency: c, Buffer: b}
}

// Type aliases
type BifrostEmbeddingRequest = EmbeddingRequest
type BifrostEmbeddingResponse = EmbeddingResponse
type TextCompletionRequest = CompletionRequest
type BifrostChatResponse = ChatResponse

// Constants
const ProviderKey = "voyage"

// GraphQL Complexity type (4 args WITH context for voyage)
// GraphQL Complexity type (4 args, NO context)
// GraphQL Complexity type (4 args, NO context for gqlgen)
type Complexity func(op string, varName string, depth int, args map[string]any) (int, bool)

// Fixed Plugin interface with correct signatures
type Plugin interface {
	GetName() string
	Config() map[string]interface{}
	TransportInterceptor(ctx context.Context, req *BifrostRequest) (*BifrostRequest, error)
	PreHook(ctx context.Context, req *BifrostRequest) (*BifrostRequest, error)
	PostHook(ctx context.Context, resp *BifrostResponse) error
	Cleanup() error
}

// Alternative Plugin with TransportInterceptor returning error
type PluginWithError interface {
	GetName() string
	Config() map[string]interface{}
	TransportInterceptor(ctx context.Context, req *BifrostRequest) (*BifrostRequest, *BifrostError, error)
	PreHook(ctx context.Context, req *BifrostRequest) (*BifrostRequest, error)
	PostHook(ctx context.Context, resp *BifrostResponse) error
	Cleanup() error
}

// ConcurrencyAndBuffer with BufferSize field
type ConcurrencyAndBuffer struct {
	Concurrency int `json:"concurrency"`
	Buffer     int `json:"buffer"`
	BufferSize int `json:"buffer_size,omitempty"`
}

type ConcurrencyAndBufferSize struct {
	Concurrency int `json:"concurrency"`
	Buffer     int `json:"buffer"`
	BufferSize int `json:"buffer_size,omitempty"`
}

func NewConcurrencyAndBuffer(c, b int) ConcurrencyAndBuffer {
	return ConcurrencyAndBuffer{Concurrency: c, Buffer: b}
}

func (c ConcurrencyAndBuffer) GetConcurrency() int { return c.Concurrency }
func (c ConcurrencyAndBuffer) GetBufferSize() int { return c.Buffer }

// NetworkConfig with methods
func (nc NetworkConfig) GetDefaultRequestTimeoutInSeconds() int {
	return 30
}

func (nc NetworkConfig) GetRetryBackoffInitial() time.Duration {
	return nc.RetryBackoff
}

func (nc NetworkConfig) GetRetryBackoffMax() time.Duration {
	return nc.RetryBackoff * 2
}

// ProviderConfig with NetworkConfig pointer
type ProviderConfig struct {
	Provider               Provider                 `json:"provider"`
	BaseURL                string                  `json:"base_url"`
	APIKey                 string                  `json:"api_key,omitempty"`
	Timeout                time.Duration           `json:"timeout"`
	Headers                map[string]string       `json:"headers"`
	ExtraParams            map[string]interface{}   `json:"extra_params"`
	ConcurrencyAndBuffer  ConcurrencyAndBuffer    `json:"concurrency_and_buffer,omitempty"`
	BufferSize            int                    `json:"buffer_size,omitempty"`
	NetworkConfig         *NetworkConfig         `json:"network_config,omitempty"`
	Dimensions            int                    `json:"dimensions,omitempty"`
}

// Bifrost type
type Bifrost struct {
	config *BifrostConfig
}

func NewBifrost(cfg *BifrostConfig) *Bifrost {
	return &Bifrost{config: cfg}
}

// BifrostEmbeddingRequest
type BifrostEmbeddingRequest = EmbeddingRequest

// BifrostEmbeddingResponse with Object field
type BifrostEmbeddingResponse struct {
	Data  []EmbeddingData `json:"data"`
	Model string         `json:"model"`
	Usage Usage          `json:"usage"`
	Object string        `json:"object,omitempty"`
}

// TextCompletionRequest alias
type TextCompletionRequest = CompletionRequest

// ChatMessageRoleSystem constant
const ChatMessageRoleSystem = ChatMessageRole("system")
