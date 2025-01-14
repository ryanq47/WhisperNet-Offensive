#!/bin/bash

API_URL="http://127.0.0.1:8081"
# Yes - default creds, this is fine
USERNAME="username"  # Replace with your credentials or load from .env
PASSWORD="password"

# Fetch the JWT token
echo "Fetching JWT token..."
response=$(curl -s -X POST "${API_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "'"${USERNAME}"'", "password": "'"${PASSWORD}"'"}')

# Extract the token from the response
TOKEN=$(echo "$response" | jq -r '.data.access_token')

# Check if the token was fetched successfully
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Failed to retrieve JWT token. Response: $response"
    exit 1
fi

echo "JWT token fetched successfully."

schemathesis run $API_URL/swagger.json -H "Authorization: Bearer $TOKEN" 