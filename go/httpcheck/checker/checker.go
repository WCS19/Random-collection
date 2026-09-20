package checker

import (
	"context"
	"net/http"
	"time"
)

// Result is the outcome of a single URL check.
type Result struct {
	URL        string
	StatusCode int
	OK         bool
	Latency    time.Duration
	Error      string
}

// Check fetches url with a timeout and records status + latency.
func Check(ctx context.Context, client *http.Client, url string) Result {
	start := time.Now()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return Result{URL: url, Error: err.Error(), Latency: time.Since(start)}
	}

	resp, err := client.Do(req)
	latency := time.Since(start)
	if err != nil {
		return Result{URL: url, Error: err.Error(), Latency: latency}
	}
	defer resp.Body.Close()

	return Result{
		URL:        url,
		StatusCode: resp.StatusCode,
		OK:         resp.StatusCode >= 200 && resp.StatusCode < 400,
		Latency:    latency,
	}
}
