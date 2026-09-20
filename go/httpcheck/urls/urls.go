package urls

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// Normalize ensures the URL has a scheme.
func Normalize(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return ""
	}
	if !strings.Contains(raw, "://") {
		return "https://" + raw
	}
	return raw
}

// FromArgs collects URLs from CLI args (skips flag-like tokens).
func FromArgs(args []string) []string {
	var out []string
	for _, a := range args {
		if strings.HasPrefix(a, "-") {
			continue
		}
		if u := Normalize(a); u != "" {
			out = append(out, u)
		}
	}
	return out
}

// FromFile reads one URL per line (ignores blanks and # comments).
func FromFile(path string) ([]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open %s: %w", path, err)
	}
	defer f.Close()

	var out []string
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		out = append(out, Normalize(line))
	}
	return out, sc.Err()
}
