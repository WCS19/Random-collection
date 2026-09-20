package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"sort"
	"time"

	"httpcheck/checker"
	"httpcheck/urls"
)

func main() {
	workers := flag.Int("workers", 16, "max concurrent requests")
	timeout := flag.Duration("timeout", 5*time.Second, "per-request timeout")
	file := flag.String("file", "", "optional file with one URL per line")
	flag.Parse()

	list := urls.FromArgs(flag.Args())
	if *file != "" {
		fromFile, err := urls.FromFile(*file)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		list = append(list, fromFile...)
	}

	if len(list) == 0 {
		fmt.Fprintf(os.Stderr, "usage: httpcheck [flags] <url> [url...]\n")
		fmt.Fprintf(os.Stderr, "       httpcheck -file urls.txt\n")
		flag.PrintDefaults()
		os.Exit(2)
	}

	ctx := context.Background()
	start := time.Now()
	results := checker.Run(ctx, list, *workers, *timeout)
	elapsed := time.Since(start)

	sort.Slice(results, func(i, j int) bool {
		return results[i].URL < results[j].URL
	})

	okCount := 0
	for _, r := range results {
		printResult(r)
		if r.OK {
			okCount++
		}
	}

	fmt.Printf("\n%d/%d ok in %v (%d workers)\n", okCount, len(results), elapsed.Round(time.Millisecond), *workers)
	if okCount != len(results) {
		os.Exit(1)
	}
}

func printResult(r checker.Result) {
	if r.Error != "" {
		fmt.Printf("FAIL  %-40s  %8v  %s\n", r.URL, r.Latency.Round(time.Millisecond), r.Error)
		return
	}
	status := "OK  "
	if !r.OK {
		status = "FAIL"
	}
	fmt.Printf("%s  %-40s  %3d  %8v\n", status, r.URL, r.StatusCode, r.Latency.Round(time.Millisecond))
}
