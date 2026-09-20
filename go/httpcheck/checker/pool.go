package checker

import (
	"context"
	"net/http"
	"sync"
	"time"
)

// Run checks all urls concurrently, bounded by workers.
func Run(ctx context.Context, urls []string, workers int, timeout time.Duration) []Result {
	if workers < 1 {
		workers = 1
	}

	client := &http.Client{
		Timeout: timeout,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 5 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}

	jobs := make(chan string)
	results := make(chan Result, len(urls))

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for url := range jobs {
				results <- Check(ctx, client, url)
			}
		}()
	}

	go func() {
		defer close(jobs)
		for _, u := range urls {
			select {
			case <-ctx.Done():
				return
			case jobs <- u:
			}
		}
	}()

	go func() {
		wg.Wait()
		close(results)
	}()

	out := make([]Result, 0, len(urls))
	for r := range results {
		out = append(out, r)
	}
	return out
}
