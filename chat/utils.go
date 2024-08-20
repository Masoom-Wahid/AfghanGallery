package main

import (
	"fmt"
	"log"

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
