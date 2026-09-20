package calc_test

import (
	"testing"

	"calculator/calc"
)

func TestEvaluate(t *testing.T) {
	cases := []struct {
		expr string
		want float64
	}{
		{"1+2", 3},
		{"10-3", 7},
		{"4*5", 20},
		{"20/4", 5},
		{"2+3*4", 14},
		{"(2+3)*4", 20},
		{"-5+2", -3},
		{"3.5+1.5", 5},
		{"(1+2)*(3+4)", 21},
	}

	for _, c := range cases {
		got, err := calc.Evaluate(c.expr)
		if err != nil {
			t.Fatalf("%q: unexpected error: %v", c.expr, err)
		}
		if got != c.want {
			t.Errorf("%q: got %v, want %v", c.expr, got, c.want)
		}
	}
}

func TestDivideByZero(t *testing.T) {
	_, err := calc.Evaluate("1/0")
	if err == nil {
		t.Fatal("expected division by zero error")
	}
}
