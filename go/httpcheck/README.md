# httpcheck

Concurrent HTTP status checker in **Go** and **Python**, side by side with the same flags, similar output, so I could compare.

Python uses `ThreadPoolExecutor` + stdlib `urllib` (no extra deps). Go uses goroutines + `net/http`.

## Layout

```
httpcheck/
├── main.go              # Go CLI
├── go.mod
├── httpcheck.py         # Python twin
├── server/main.go       # local bench HTTP server
├── checker/
│   ├── checker.go
│   ├── pool.go
│   └── checker_test.go
├── urls/
│   └── urls.go
├── urls.example.txt     # remote URLs (noisy)
└── urls.local.txt       # hit the local server
```

## Local bench server

Start this in one terminal (keeps running):

```bash
cd go/httpcheck
go run ./server
# listens on http://127.0.0.1:8080
```

Endpoints: `/ok`, `/status/{code}`, `/slow` (50ms), `/delay/{ms}`.

Then compare against it (no internet jitter):

```bash
# other terminal, same directory
echo '=== Go ===' && go run . -workers 8 -timeout 2s -file urls.local.txt
echo '=== Python ===' && python httpcheck.py -workers 8 -timeout 2 -file urls.local.txt
```

## Run Go (remote)

```bash
cd go/httpcheck
go run . -file urls.example.txt
go build -o httpcheck .
./httpcheck -file urls.example.txt
```

## Run Python (remote)

```bash
cd go/httpcheck
python httpcheck.py -file urls.example.txt
```

## Tests (Go)

```bash
go test ./...
```

## Why this exists

Side-by-side Go and Python workers hitting the same URLs so I can feel
the difference: goroutines + a single binary vs threads + an interpreter.
For remote HTTP, network latency usually dominates; the local bench server
makes the runtime/concurrency comparison clearer.
