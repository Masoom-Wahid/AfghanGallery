package main

import (
	"database/sql"
	"log"
	"time"
)

type User struct {
	ID       int    `json:"id"`
	Email    string `json:"email"`
	Verified bool   `json:"verified"`
}

// TODO: add SenderEmail and ReceiverEmail fields and make them functional
// adding them from redis is easy , just edit the query from the db to not get only the sender_id and receiver_id
// but also the sender_email and receiver_email
type Message struct {
	Msg           string `json:"msg"`
	Sender        int    `json:"sender"`
	SenderEmail   string `json:"sender_email"`
	Receiver      int    `json:"receiver"`
	ReceiverEmail string `json:"receiver_email"`
	Time          string `json:"time"`
}

func save_msg_to_db(msgs []Message, room_id string) error {
	tx, err := DB.Begin()
	if err != nil {
		return err
	}
	stmt, err := tx.Prepare(`
		INSERT INTO user_message (
			msg, created_at, updated_at, receiver_id, sender_id,room_id_id
		) VALUES (
			?, ?, ?, ?, ?,?
		)
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for _, msg := range msgs {
		_, err := stmt.Exec(
			msg.Msg,
			msg.Time,
			msg.Time,
			msg.Receiver,
			msg.Sender,
			room_id,
		)
		if err != nil {
			log.Println(err)
			return tx.Rollback()
		}
	}
	if err := tx.Commit(); err != nil {
		return err
	}
	return nil
}

func get_user_instance(email string) (*User, error) {
	sqlstmt := `
        SELECT id, email, is_verified FROM user_customuser WHERE email = ?
    `

	row := DB.QueryRow(sqlstmt, email)

	var user User
	err := row.Scan(&user.ID, &user.Email, &user.Verified)
	if err == sql.ErrNoRows {
		println(err.Error())
		return nil, nil
	} else if err != nil {
		println(err.Error())
		// Error occurred while querying the database
		return nil, err
	}

	// User found
	return &user, nil
}

func create_room(user1, user2 int) (int, error) {
	time_now := time.Now()
	sqlstmt := "INSERT INTO user_room (user1_id, user2_id,created_at,updated_at) VALUES (?, ?,?,?)"
	result, err := DB.Exec(sqlstmt, user1, user2, time_now, time_now)
	if err != nil {
		return 0, err
	}
	id, err := result.LastInsertId()
	if err != nil {
		return 0, err
	}
	return int(id), nil
}

func get_room(user1, user2 int) (int, error) {
	sqlstmt := `
			SELECT id
			FROM user_room
			WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
		`
	row := DB.QueryRow(sqlstmt, user1, user2, user2, user1)
	var id int
	err := row.Scan(&id)
	if err == sql.ErrNoRows {
		return 0, err

	} else if err != nil {
		return 0, err
	}
	return id, nil
}

func get_msgs_of_room(roomID string) ([]Message, error) {
	stmt := `
		SELECT msg,sender_id,receiver_id,created_at,updated_at
		FROM user_message
		WHERE room_id_id = ?
		ORDER_BY created_at DESC
	`

	rows, err := DB.Query(stmt, roomID)
	if err != nil {
		return nil, err
	}

	defer rows.Close()

	var msgs []Message

	for rows.Next() {
		var msg Message
		if err := rows.Scan(&msg.Msg, &msg.Sender, &msg.Receiver, &msg.Time); err != nil {
			return nil, err

		}
		msgs = append(msgs, msg)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return msgs, nil

}
