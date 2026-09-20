package calc

import (
	"fmt"

	"calculator/ops"
	"calculator/parser"
)

// Evaluate parses and evaluates a math expression.
// Supports + - * / and parentheses. * and / bind tighter than + and -.
func Evaluate(expr string) (float64, error) {
	tokens, err := parser.Tokenize(expr)
	if err != nil {
		return 0, err
	}
	p := &parserState{tokens: tokens, pos: 0}
	result, err := p.parseExpr()
	if err != nil {
		return 0, err
	}
	if p.current().Kind != parser.EOF {
		return 0, fmt.Errorf("unexpected token %q", p.current().Raw)
	}
	return result, nil
}

type parserState struct {
	tokens []parser.Token
	pos    int
}

func (p *parserState) current() parser.Token {
	return p.tokens[p.pos]
}

func (p *parserState) advance() parser.Token {
	t := p.tokens[p.pos]
	if t.Kind != parser.EOF {
		p.pos++
	}
	return t
}

// expr = term ((+|-) term)*
func (p *parserState) parseExpr() (float64, error) {
	left, err := p.parseTerm()
	if err != nil {
		return 0, err
	}

	for {
		switch p.current().Kind {
		case parser.Plus:
			p.advance()
			right, err := p.parseTerm()
			if err != nil {
				return 0, err
			}
			left = ops.Add(left, right)
		case parser.Minus:
			p.advance()
			right, err := p.parseTerm()
			if err != nil {
				return 0, err
			}
			left = ops.Sub(left, right)
		default:
			return left, nil
		}
	}
}

// term = factor ((*|/) factor)*
func (p *parserState) parseTerm() (float64, error) {
	left, err := p.parseFactor()
	if err != nil {
		return 0, err
	}

	for {
		switch p.current().Kind {
		case parser.Star:
			p.advance()
			right, err := p.parseFactor()
			if err != nil {
				return 0, err
			}
			left = ops.Mul(left, right)
		case parser.Slash:
			p.advance()
			right, err := p.parseFactor()
			if err != nil {
				return 0, err
			}
			left, err = ops.Div(left, right)
			if err != nil {
				return 0, err
			}
		default:
			return left, nil
		}
	}
}

// factor = number | '(' expr ')' | '-' factor
func (p *parserState) parseFactor() (float64, error) {
	switch p.current().Kind {
	case parser.Number:
		return p.advance().Value, nil
	case parser.Minus:
		p.advance()
		v, err := p.parseFactor()
		if err != nil {
			return 0, err
		}
		return -v, nil
	case parser.LParen:
		p.advance()
		v, err := p.parseExpr()
		if err != nil {
			return 0, err
		}
		if p.current().Kind != parser.RParen {
			return 0, fmt.Errorf("expected ')'")
		}
		p.advance()
		return v, nil
	default:
		return 0, fmt.Errorf("expected number or '(', got %q", p.current().Raw)
	}
}
