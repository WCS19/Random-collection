package parser

import (
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

// Token kinds for a simple expression lexer.
type Kind int

const (
	Number Kind = iota
	Plus
	Minus
	Star
	Slash
	LParen
	RParen
	EOF
)

type Token struct {
	Kind  Kind
	Value float64 // only for Number
	Raw   string
}

// Tokenize splits an expression into tokens.
// Supports: numbers (incl. decimals), + - * / ( )
func Tokenize(input string) ([]Token, error) {
	input = strings.TrimSpace(input)
	var tokens []Token
	i := 0

	for i < len(input) {
		ch := rune(input[i])

		if unicode.IsSpace(ch) {
			i++
			continue
		}

		switch ch {
		case '+':
			tokens = append(tokens, Token{Kind: Plus, Raw: "+"})
			i++
		case '-':
			tokens = append(tokens, Token{Kind: Minus, Raw: "-"})
			i++
		case '*':
			tokens = append(tokens, Token{Kind: Star, Raw: "*"})
			i++
		case '/':
			tokens = append(tokens, Token{Kind: Slash, Raw: "/"})
			i++
		case '(':
			tokens = append(tokens, Token{Kind: LParen, Raw: "("})
			i++
		case ')':
			tokens = append(tokens, Token{Kind: RParen, Raw: ")"})
			i++
		default:
			if unicode.IsDigit(ch) || ch == '.' {
				start := i
				for i < len(input) {
					c := rune(input[i])
					if unicode.IsDigit(c) || c == '.' {
						i++
						continue
					}
					break
				}
				raw := input[start:i]
				n, err := strconv.ParseFloat(raw, 64)
				if err != nil {
					return nil, fmt.Errorf("invalid number %q", raw)
				}
				tokens = append(tokens, Token{Kind: Number, Value: n, Raw: raw})
			} else {
				return nil, fmt.Errorf("unexpected character %q at position %d", string(ch), i)
			}
		}
	}

	tokens = append(tokens, Token{Kind: EOF, Raw: ""})
	return tokens, nil
}
