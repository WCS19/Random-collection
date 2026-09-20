package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"
)

func main() {
	addr := flag.String("addr", "127.0.0.1:8080", "listen address")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/", handleRoot)
	mux.HandleFunc("/ok", handleOK)
	mux.HandleFunc("/status/", handleStatus)
	mux.HandleFunc("/slow", handleSlow)
	mux.HandleFunc("/delay/", handleDelay)

	fmt.Printf("httpcheck bench server on http://%s\n", *addr)
	fmt.Println("  GET /ok")
	fmt.Println("  GET /status/{code}   e.g. /status/404")
	fmt.Println("  GET /slow            200 after 50ms")
	fmt.Println("  GET /delay/{ms}      200 after N ms")
	log.Fatal(http.ListenAndServe(*addr, mux))
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "text/plain")
	fmt.Fprintln(w, "httpcheck local bench server")
}

func handleOK(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "ok")
}

func handleStatus(w http.ResponseWriter, r *http.Request) {
	codeStr := strings.TrimPrefix(r.URL.Path, "/status/")
	code, err := strconv.Atoi(codeStr)
	if err != nil || code < 100 || code > 599 {
		http.Error(w, "bad status code", http.StatusBadRequest)
		return
	}
	w.WriteHeader(code)
	fmt.Fprintf(w, "status %d", code)
}

func handleSlow(w http.ResponseWriter, r *http.Request) {
	time.Sleep(50 * time.Millisecond)
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "slow")
}

func handleDelay(w http.ResponseWriter, r *http.Request) {
	msStr := strings.TrimPrefix(r.URL.Path, "/delay/")
	ms, err := strconv.Atoi(msStr)
	if err != nil || ms < 0 || ms > 60_000 {
		http.Error(w, "bad delay", http.StatusBadRequest)
		return
	}
	time.Sleep(time.Duration(ms) * time.Millisecond)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "delayed %dms", ms)
}
