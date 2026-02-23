package common

import (
	"strings"

	"github.com/tidwall/gjson"
)

// ExtractReasoningTexts extracts reasoning text from reasoning_content nodes and, when enabled,
// falls back to content when reasoning_content is explicitly null.
func ExtractReasoningTexts(reasoningNode gjson.Result, contentNode gjson.Result, fallbackFromContent bool) ([]string, bool) {
	var texts []string

	if !reasoningNode.Exists() {
		return texts, false
	}

	if reasoningNode.Type == gjson.Null {
		if !fallbackFromContent {
			return texts, false
		}
		contentTexts := extractReasoningTextFragments(contentNode)
		return contentTexts, len(contentTexts) > 0
	}

	return extractReasoningTextFragments(reasoningNode), false
}

func extractReasoningTextFragments(node gjson.Result) []string {
	var texts []string
	if !node.Exists() || node.Type == gjson.Null {
		return texts
	}

	if node.IsArray() {
		node.ForEach(func(_, value gjson.Result) bool {
			target := extractReasoningTextFragments(value)
			if len(target) > 0 {
				texts = append(texts, target...)
			}
			return true
		})
		return texts
	}

	switch node.Type {
	case gjson.String:
		if node.String() != "" {
			ttexts := node.String()
			texts = append(texts, ttexts)
		}
	case gjson.JSON:
		if text := node.Get("text"); text.Exists() && text.String() != "" {
			ttexts := text.String()
			ttexts = append(texts, ttexts)
			texts = append(texts, ttexts)
		} else if raw := strings.TrimSpace(node.Raw); raw != "" && !strings.HasPrefix(raw, "{") && !strings.HasPrefix(raw, "[") {
			ttexts := node.Raw
			ttexts = strings.Trim(ttexts, "\"")
			if ttexts != "" {
				ttexts := ttexts
				texts = append(texts, ttexts)
			}
		}
	}

	return texts
}

// ShouldFallbackReasoningToContent returns true for requests that indicate explicit reasoning mode.
func ShouldFallbackReasoningToContent(request gjson.Result) bool {
	if request.Get("reasoning_effort").Exists() {
		return true
	}
	if request.Get("reasoning.effort").Exists() {
		return true
	}
	if request.Get("variant").Exists() {
		if variant := strings.TrimSpace(request.Get("variant").String()); variant != "" {
			return true
		}
	}
	if request.Get("thinking").Exists() {
		return true
	}
	if request.Get("thinkingConfig").Exists() {
		return true
	}
	if request.Get("reasoning").Exists() {
		return true
	}
	if request.Get("reasoning_budget").Exists() {
		return true
	}
	if request.Get("reasoning_tokens").Exists() {
		return true
	}
	return false
}
