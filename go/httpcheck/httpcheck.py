#!/usr/bin/env python3
"""Python twin of the Go httpcheck CLI — same flags and output shape for comparison."""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class Result:
    url: str
    status_code: int = 0
    ok: bool = False
    latency_ms: int = 0
    error: str = ""


def normalize(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if "://" not in raw:
        return "https://" + raw
    return raw


def from_file(path: str) -> list[str]:
    out: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            out.append(normalize(line))
    return out


def check(url: str, timeout: float) -> Result:
    start = time.perf_counter()
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return Result(
                url=url,
                status_code=code,
                ok=200 <= code < 400,
                latency_ms=latency_ms,
            )
    except HTTPError as e:
        # urllib raises on 4xx/5xx but still has a status code
        latency_ms = int((time.perf_counter() - start) * 1000)
        return Result(
            url=url,
            status_code=e.code,
            ok=200 <= e.code < 400,
            latency_ms=latency_ms,
        )
    except (URLError, TimeoutError, OSError) as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        reason = getattr(e, "reason", e)
        return Result(url=url, latency_ms=latency_ms, error=str(reason))


def run(urls: list[str], workers: int, timeout: float) -> list[Result]:
    workers = max(1, workers)
    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check, u, timeout): u for u in urls}
        for fut in as_completed(futures):
            results.append(fut.result())
    return results


def print_result(r: Result) -> None:
    latency = f"{r.latency_ms}ms"
    if r.error:
        print(f"FAIL  {r.url:<40}  {latency:>8}  {r.error}")
        return
    status = "OK  " if r.ok else "FAIL"
    print(f"{status}  {r.url:<40}  {r.status_code:3d}  {latency:>8}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Concurrent HTTP status checker (Python)")
    parser.add_argument("urls", nargs="*", help="URLs to check")
    parser.add_argument("-workers", "--workers", type=int, default=16, help="max concurrent requests")
    parser.add_argument(
        "-timeout",
        "--timeout",
        type=float,
        default=5.0,
        help="per-request timeout in seconds",
    )
    parser.add_argument("-file", "--file", default="", help="file with one URL per line")
    args = parser.parse_args()

    list_urls = [normalize(u) for u in args.urls if normalize(u)]
    if args.file:
        try:
            list_urls.extend(from_file(args.file))
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1

    if not list_urls:
        parser.print_help()
        return 2

    start = time.perf_counter()
    results = run(list_urls, args.workers, args.timeout)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    results.sort(key=lambda r: r.url)
    ok_count = 0
    for r in results:
        print_result(r)
        if r.ok:
            ok_count += 1

    print(f"\n{ok_count}/{len(results)} ok in {elapsed_ms}ms ({args.workers} workers)")
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
