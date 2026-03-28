package main

import (
	"log"

	"github.com/KooshaPari/pheno-session/cmd"
)

func main() {
	if err := cmd.Execute(); err != nil {
		log.Fatalf("pheno-session: %v", err)
	}
}
