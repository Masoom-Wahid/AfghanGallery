package main

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

/*
A golabl variable and a function to start the thing,
we set the max open connections to 10 , just in case although sqlite3
does have a lock on writes
*/
var DB *sql.DB

func InitDB(path string) {
	var err error
	DB, err = sql.Open("sqlite3", path)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	DB.SetMaxOpenConns(10)
}

func saveMessagesToDB(roomID string) {
	// Retrieve all messages from Redis list
	// Log all messages
	chatMessages := get_msgs_from_redis(roomID)
	save_msg_to_db(chatMessages, roomID)
}