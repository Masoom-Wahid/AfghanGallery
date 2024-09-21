package main

import (
	"context"
	"encoding/json"
	"fmt"
	socketio "github.com/googollee/go-socket.io"
	"github.com/joho/godotenv"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

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

var (
	ctx             = context.Background()
	secretKey       []byte
	roomMutex       sync.Mutex
	roomConnections = make(map[string]int)
	connections     = make(map[int]int)
	secret_key      []byte
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	secret_key_var := os.Getenv("SECRET_KEY")
	if secret_key_var == "" {
		log.Fatalf("SECRET_KEY required")
	}
	secret_key = []byte(secret_key_var)

	Init(
		os.Getenv("DB_PATH"),
		os.Getenv("REDIS_HOST"),
		os.Getenv("REDIS_PORT"),
		os.Getenv("REDIS_PASSWORD"),
	)

	pong, err := redisClient.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}
	fmt.Println("Redis connected:", pong)
	server := socketio.NewServer(nil)

	server.OnEvent("/", "join", func(s socketio.Conn, props JoinArgs) error {
		user_ctx := s.Context().(string)
		user, err := get_user_from_ctx(user_ctx)
		if err != nil {
			s.Emit("Context Failed")
			s.Close()
			return fmt.Errorf("Context Failed")
		}
		otherEmail := props.OtherEmail
		otherUser, err := get_user_instance(otherEmail)
		if err != nil {
			s.Emit("error", "Invalid user")
			return fmt.Errorf("Invalid user")
		}

		roomId, err := get_room(user.ID, otherUser.ID)
		if err != nil {
			roomId, err = create_room(user.ID, otherUser.ID)
			if err != nil {
				s.Emit("error", "Unable to create room")
				return fmt.Errorf("Unable to create room")
			}
		}

		room := strconv.Itoa(roomId)
		prev_room := strconv.Itoa(connections[user.ID])
		save_room_state(
			prev_room,
			user,
		)

		connections[user.ID] = roomId
		s.Leave(prev_room)
		s.Join(room)

		prevMsgs, err := get_msgs_of_room(room)
		if err != nil {
			s.Emit("error", "Error fetching messages")
		}
		redisMsgs := get_msgs_from_redis(room)
		allMessages := append(redisMsgs, prevMsgs...)
		s.Emit("join", allMessages)

		roomMutex.Lock()
		roomConnections[room]++
		roomMutex.Unlock()
		return nil
	})

	server.OnEvent("/", "send_message", func(s socketio.Conn, msg MsgArgs) error {
		user, err := get_user_from_ctx(s.Context().(string))
		if err != nil {
			s.Close()
			return err
		}

		room := strconv.Itoa(connections[user.ID])
		message := Message{
			Msg:      msg.Msg,
			Time:     time.Now().Format(time.RFC3339),
			Sender:   user.ID,
			Receiver: msg.Receiver,
		}

		msgJSON, err := json.Marshal(message)
		if err != nil {
			s.Close()
			return fmt.Errorf("failed to marshal message: %v", err)
		}

		if err := redisClient.LPush(ctx, "chat:"+room, msgJSON).Err(); err != nil {
			s.Close()
			return fmt.Errorf("failed to store message in Redis: %v", err)
		}

		server.BroadcastToRoom("/", room, "receive_message", message)
		return nil
	})

	server.OnConnect("/", func(s socketio.Conn) error {
		url := s.URL()
		token := url.Query().Get("token")
		if token == "" {
			s.Close()
			return fmt.Errorf("token required")
		}

		email, err := ParseToken(token)
		if err != nil {
			s.Close()
			return fmt.Errorf("invalid token")
		}

		user, err := get_user_instance(email)
		if err != nil || user == nil || !user.Verified {
			s.Close()
			return fmt.Errorf("unauthorized")
		}

		user_ctx := fmt.Sprintf("%v %v %v", user.ID, user.Email, user.Verified)
		s.SetContext(user_ctx)
		return nil
	})

	server.OnDisconnect("/", func(s socketio.Conn, reason string) {
		user_interface := s.Context()
		if user_interface == nil {
			return
		}

		user, err := get_user_from_ctx(user_interface.(string))
		if err != nil {
			s.LeaveAll()
			return
		}

		room := connections[user.ID]
		if room != 0 {
			save_room_state(
				strconv.Itoa(connections[user.ID]),
				user,
			)
		}

		delete(connections, user.ID)
		s.LeaveAll()
	})

	go server.Serve()
	defer server.Close()

	port := os.Getenv("PORT")
	http.Handle("/ws/", server)
	log.Printf("Socket.IO server started on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
