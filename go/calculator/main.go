package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"calculator/calc"
)

func main() {
	if len(os.Args) > 1 {
		expr := strings.Join(os.Args[1:], " ")
		printResult(expr)
		return
	}

	fmt.Println("Go calculator — enter expressions (+ - * / and parentheses)")
	fmt.Println("Type 'quit' or 'exit' to leave.")
	fmt.Println()

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if line == "quit" || line == "exit" {
			break
		}
		printResult(line)
	}
}

func printResult(expr string) {
	result, err := calc.Evaluate(expr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		return
	}
	fmt.Println(result)
}
