package checker_test

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"httpcheck/checker"
)

func TestCheckOK(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	client := &http.Client{Timeout: 2 * time.Second}
	r := checker.Check(context.Background(), client, srv.URL)
	if !r.OK || r.StatusCode != 200 {
		t.Fatalf("expected OK/200, got %+v", r)
	}
}

func TestRunConcurrent(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(20 * time.Millisecond)
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	urls := []string{srv.URL, srv.URL, srv.URL, srv.URL}
	start := time.Now()
	results := checker.Run(context.Background(), urls, 4, 2*time.Second)
	elapsed := time.Since(start)

	if len(results) != 4 {
		t.Fatalf("got %d results, want 4", len(results))
	}
	// Sequential would be ~80ms+; concurrent should finish closer to one sleep.
	if elapsed > 150*time.Millisecond {
		t.Fatalf("expected concurrent speedup, took %v", elapsed)
	}
}
