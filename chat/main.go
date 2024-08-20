package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
)

var (
	// an HTTP to websocket upgrade
	upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool { return true }}
	ctx      = context.Background()
	debug    string
	// Tracks active connections per room
	roomConnections = make(map[string]int)
	// To ensure thread-safe operations on roomConnections
	roomMutex  sync.Mutex
	secret_key []byte
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Err loading.env file")
	}
	secret_key_var := os.Getenv("SECRET_KEY")
	if secret_key_var == "" {
		log.Fatalf("SECRET_KEY required")
	}
	secret_key = []byte(secret_key_var)
	debug = os.Getenv("DEBUG")
	Init(
		os.Getenv("DB_PATH"),
		os.Getenv("REDIS_HOST"),
		os.Getenv("REDIS_PORT"),
		os.Getenv("REDIS_PASSWORD"),
	)
	http.HandleFunc("/ws", handleWebSocket)

	portnumber, err := strconv.ParseInt(os.Getenv("PORT"), 10, 64)
	if err != nil {
		log.Fatalf("Invalid port value %v\n", err)
	}

	port := fmt.Sprintf(":%d", portnumber)

	log.Printf("Chat WebSocket server started on %s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	/*

		we need 2 things before we can start letting users to chat
		first a token (the users token) and then the email of the user they want to talk to
		the initiator must be 'verified' or else we do not allow him to talk


		so it looks smth like

		ws://localhost:8080?token={token}&email={email}

		we parse the token and get the user's email => check if it exists in the db
		and we do the same for the other_user's email

		after all said and done we let the user initiate a chat
		BUT:
			since we only store the msgs on db when a room dies
			we have to handle the case of msgs being most in db and some in redis
			the logic is this:
				we keep an mutex of rooms_participants
				until a room has persons chatting we keep the data in redis
				why ? because of speed (although i could also just save it to db but my 'ego' i guess)
				so what happends if a room has no person anymore ?
				we just simply get all the data from redis and then shove em all in db
				BUT:
					what happens if a user joins a room when another user is already there?
					some of the data is still in redis right?
					for that we fetch all msgs in db first and then fetch all the msgs from redis
					and then we merge them , and there  you go , you have all ur msgs

			we create a goroutine for the listener of a user and then let the sync code to listen for the
			inputs of the user
			we just want {
				"msg" : "msg"
			}
			since we already know who is who

	*/

	token := r.URL.Query().Get("token")
	other_email := r.URL.Query().Get("email")
	if token == "" || other_email == "" {
		writeResponse("no token and email", "token and email required", w)
		return
	}
	user_email, err := ParseToken(token)
	if err != nil {
		writeResponse("can't parse token", "no valid token", w)
		return
	}

	user, err := get_user_instance(user_email)
	// if no user or some err or is not verified then we do not want them talk
	if user == nil || err != nil || !user.Verified {
		writeResponse("the first user isnt real", "invalid token info", w)
		return
	}

	other_user, err := get_user_instance(other_email)
	if other_user == nil || err != nil {
		writeResponse("the second user isnt real", "invalid token info", w)
		return
	}

	room_id, err := get_room(user.ID, other_user.ID)
	if err != nil {
		room_id, err = create_room(user.ID, other_user.ID)
		if err != nil {
			writeResponse("couldnt create a room", "err when creating a room", w)
			return
		}
	}

	room := strconv.Itoa(room_id)
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}
	defer conn.Close()

	pubsub := redisClient.Subscribe(ctx, room)
	defer pubsub.Close()

	/*
		get the prev msgs from the db first and then handle the msgs which are in redis
		and then send them all
	*/
	prev_msgs, _ := get_msgs_of_room(room)
	roomMutex.Lock()
	if roomConnections[room] > 0 {
		redis_msgs := get_msgs_from_redis(room)
		prev_msgs = append(prev_msgs, redis_msgs...)
	}
	conn.WriteJSON(prev_msgs)
	roomConnections[room]++
	roomMutex.Unlock()

	// Goroutine to listen for messages from Redis
	go func() {
		for {
			msg, err := pubsub.ReceiveMessage(ctx)
			if err != nil {
				return
			}

			var message Message
			if err := json.Unmarshal([]byte(msg.Payload), &message); err != nil {
				continue
			}

			if err := conn.WriteJSON(message); err != nil {
				return
			}
		}
	}()

	for {
		_, msg, err := conn.ReadMessage()
		if err != nil {
			break
		}

		var message Message
		if err := json.Unmarshal(msg, &message); err != nil {
			continue
		}

		if message.Msg == "" {
			continue
		}
		message.Time = time.Now().Format(time.RFC3339)
		message.Sender = user.ID
		message.Receiver = other_user.ID
		msgJSON, err := json.Marshal(message)
		if err != nil {
			continue
		}
		// Store the message in Redis
		if err := redisClient.LPush(ctx, "chat:"+room, msgJSON).Err(); err != nil {
			break
		}

		// Publish the message to other subscribers
		if err := redisClient.Publish(ctx, room, msgJSON).Err(); err != nil {
			break
		}
	}

	roomMutex.Lock()
	roomConnections[room]--
	if roomConnections[room] == 0 {
		saveMessagesToDB(room)
		redisClient.Del(ctx, "chat:"+room) // Clean up Redis list after saving
		delete(roomConnections, room)
	}
	roomMutex.Unlock()
}
