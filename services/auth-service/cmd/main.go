package main

import (
	"fmt"
	"log"
	"net/http"

	"auth-service/internal/config"
	"auth-service/internal/handlers"
	"auth-service/internal/repository"
	"auth-service/internal/services"
)

func main() {
	cfg := config.LoadConfig()

	repo, err := repository.NewUserRepository(cfg.GetDSN())
	if err != nil {
		log.Printf("Repository warning: %v", err)
	}

	authService := services.NewAuthService(repo, cfg.JWTSecret)
	authHandler := handlers.NewAuthHandler(authService)

	mux := http.NewServeMux()
	mux.HandleFunc("POST /api/auth/login", authHandler.Login)
	mux.HandleFunc("POST /api/auth/register", authHandler.Register)
	mux.HandleFunc("GET /api/auth/health", authHandler.Health)

	// Fallback path matching for standard http server
	mux.HandleFunc("/api/auth/login", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			authHandler.Login(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/auth/register", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			authHandler.Register(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/auth/health", func(w http.ResponseWriter, r *http.Request) {
		authHandler.Health(w, r)
	})
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		authHandler.Health(w, r)
	})

	serverAddr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("=================================")
	log.Printf("🔐 Auth Service (Go) running on %s", serverAddr)
	log.Printf("=================================")

	if err := http.ListenAndServe(serverAddr, mux); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
