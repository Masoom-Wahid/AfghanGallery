package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/go-redis/redis/v8"
)

var redisClient *redis.Client

func InitRedis(redis_host, redis_port, redis_password string) {
	redis_addr := fmt.Sprintf("%s:%s", redis_host, redis_port)
	redisClient = redis.NewClient(&redis.Options{
		Addr:     redis_addr,
		Password: redis_password,
	})

	_, err := redisClient.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
}

func Init(
	DB_path,
	Redis_host,
	Redis_port,
	Redis_password string,
) {

	InitRedis(
		Redis_host,
		Redis_port,
		Redis_password,
	)
	InitDB(
		DB_path,
	)
}

func writeResponse(from string, detail string, _ http.ResponseWriter) {
	// Cant write response
	fmt.Printf("here with from %s\nand detail %s\n", from, detail)
	// response := map[string]string{
	// 	"from":   from,
	// 	"detail": detail,
	// }

	// // Set the status code and content type
	// w.WriteHeader(http.StatusBadRequest)
	// w.Header().Set("Content-Type", "application/json")

	// // Write the JSON response
	// if err := json.NewEncoder(w).Encode(response); err != nil {
	// 	log.Printf("Failed to write JSON response: %v", err)
	// }
}
