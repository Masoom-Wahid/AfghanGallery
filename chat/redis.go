package main

import (
	"encoding/json"
	"log"
)

func get_msgs_from_redis(roomID string) []Message {
	messages, err := redisClient.LRange(ctx, "chat:"+roomID, 0, -1).Result()
	if err != nil {
		return nil
	}

	var chatMessages []Message
	for _, msg := range messages {
		var message Message
		if err := json.Unmarshal([]byte(msg), &message); err != nil {
			log.Printf("Failed to unmarshal JSON: %v", err)
			continue
		}
		chatMessages = append(chatMessages, message)
	}

	return chatMessages
}