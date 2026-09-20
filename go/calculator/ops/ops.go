package ops

import "fmt"

// Add returns a + b.
func Add(a, b float64) float64 { return a + b }

// Sub returns a - b.
func Sub(a, b float64) float64 { return a - b }

// Mul returns a * b.
func Mul(a, b float64) float64 { return a * b }

// Div returns a / b, or an error on divide-by-zero.
func Div(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}
	return a / b, nil
}
