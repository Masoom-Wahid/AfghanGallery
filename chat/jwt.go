package main

import (
	"errors"

	"github.com/dgrijalva/jwt-go"
)

func ParseToken(tokenString string) (string, error) {
	// We Start By Parsing The Token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Ensure the token's signing method (Algorithm for encoding) is what we expect
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return secret_key, nil
	})
	if err != nil {
		return "", err
	}

	// Check if the token is valid and extract the data
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		email, ok := claims["email"].(string)
		if !ok {
			return "", errors.New("invalid claims")
		}
		return string(email), nil
	}

	return "", errors.New("invalid token")
}
