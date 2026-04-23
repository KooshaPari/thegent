package cloud

import "time"

// parseRFC3339OrNow parses s as an RFC3339 timestamp.
// If s is empty or malformed, it returns time.Now().UTC() as a safe fallback.
// Used by cloud provider adapters (Netlify, Railway, etc.) when mapping
// upstream API responses that may omit or malform timestamp fields.
func parseRFC3339OrNow(s string) time.Time {
	if s == "" {
		return time.Now().UTC()
	}
	t, err := time.Parse(time.RFC3339, s)
	if err != nil {
		return time.Now().UTC()
	}
	return t
}
