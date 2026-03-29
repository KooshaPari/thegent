package bridge

import "testing"

type nopSink struct{}

func (n nopSink) Emit(event ExecutionEvent) error { return nil }

type mockAdapter struct{}

func (m mockAdapter) Execute(req ExecutionRequest) (ExecutionResponse, error) {
	return ExecutionResponse{
		BridgeSchemaVersion: "v1.0.0",
		RequestID:           req.RequestID,
		RunID:               req.RunID,
		Status:              "ok",
		SelectedRoute: SelectedRoute{
			ProviderID:    "openai",
			SubproviderID: "acct",
			Model:         "gpt-5",
		},
		Attempts: 1,
		Usage: Usage{
			InputTokens:      1,
			OutputTokens:     1,
			EstimatedCostUSD: 0.0,
		},
		Output: map[string]any{
			"message": map[string]any{
				"role":    "assistant",
				"content": "ok",
			},
			"tool_calls": []any{},
		},
		GovernanceOutcome: GovernanceOutcome{
			BudgetCheck:    "pass",
			RateLimitCheck: "pass",
			FallbackUsed:   false,
		},
	}, nil
}

func (m mockAdapter) Stream(req ExecutionRequest, sink EventSink) error {
	return sink.Emit(ExecutionEvent{
		EventType: EventDone,
		RequestID: req.RequestID,
		RunID:     req.RunID,
		AttemptID: "att_1",
		Payload:   map[string]any{"status": "ok"},
	})
}

func (m mockAdapter) Capabilities() map[string]any {
	return map[string]any{"chat_completion": true}
}

func (m mockAdapter) ResolveSubproviders(req ExecutionRequest) ([]RouteCandidate, error) {
	return []RouteCandidate{
		{
			RouteID:       "route_1",
			ProviderID:    "openai",
			SubproviderID: "acct",
			ProviderClass: "cloud_direct",
			Model:         "gpt-5",
			Priority:      100,
			Constraints: RouteConstraints{
				SupportsTools:  true,
				SupportsStream: true,
			},
		},
	}, nil
}

func TestInterfaceConformance(t *testing.T) {
	var _ EventSink = nopSink{}
	var _ ProviderAdapter = mockAdapter{}
	var _ MetaproviderAdapter = mockAdapter{}
}

