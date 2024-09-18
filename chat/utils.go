package main

import (
	"fmt"
	"log"
	"strconv"
	"strings"

	"github.com/go-redis/redis/v8"
)

var redisClient *redis.Client

type JoinArgs struct {
	OtherEmail string `json:"email"`
}
type MsgArgs struct {
	Receiver int    `json:"receiver"`
	Msg      string `json:"msg"`
}

type RoomArgs struct {
	Room string `json:"room"`
}

func get_user_from_ctx(user_ctx string) (User, error) {
	user := strings.Fields(user_ctx)
	if len(user) < 3 {
		return User{}, fmt.Errorf("invalid input format")
	}

	id, err := strconv.Atoi(user[0])
	if err != nil {
		return User{}, fmt.Errorf("failed to parse ID: %v", err)
	}

	is_verified, err := strconv.ParseBool(user[2])
	if err != nil {
		return User{}, fmt.Errorf("failed to parse is_verified: %v", err)
	}

	return User{
		ID:       id,
		Email:    user[1],
		Verified: is_verified,
	}, nil
}

func del_room(roomID int, user User) {
	if room, exists := connections[user.ID]; exists {
		if roomID == room && room != 0 {
			connections[user.ID] = 0
		}
	}
}

func save_room_state(room string, user User) {
	roomMutex.Lock()
	defer roomMutex.Unlock()
	roomConnections[room]--
	roomID, err := strconv.Atoi(room)
	if err != nil {
		return
	}
	del_room(roomID, user)
	if roomConnections[room] <= 0 {
		saveMessagesToDB(room)
		redisClient.Del(ctx, "chat:"+room)
		delete(roomConnections, room)
	}
}
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
	println("redis initited")

	InitDB(
		DB_path,
	)
	println("Database initiaed")
}
