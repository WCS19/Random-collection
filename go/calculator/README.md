# Go Calculator

Small modular expression calculator in Go.

## Layout

```
calculator/
├── main.go           # CLI entry (REPL or one-shot args)
├── go.mod
├── calc/
│   ├── calc.go       # recursive-descent evaluator
│   └── calc_test.go
├── ops/
│   └── ops.go        # Add / Sub / Mul / Div
└── parser/
    └── parser.go     # tokenizer
```

- **`ops`** — arithmetic primitives  
- **`parser`** — turns `"2+3*4"` into tokens  
- **`calc`** — parses tokens with operator precedence and parentheses  
- **`main`** — wires it into a CLI

## Install Go (macOS)

```bash
brew install go
go version   # should print something like go1.22+
```

Or download from https://go.dev/dl/

## Run locally

From this directory:

```bash
cd go/calculator

# interactive REPL
go run .

# one-shot expression
go run . '2+3*4'
go run . '(10-2)/4'
```

Build a binary:

```bash
go build -o calculator .
./calculator '1+2'
```

## Tests

```bash
go test ./...
```

## Examples

| Input | Result |
|-------|--------|
| `1+2` | `3` |
| `2+3*4` | `14` |
| `(2+3)*4` | `20` |
| `-5+2` | `-3` |
| `1/0` | error: division by zero |
