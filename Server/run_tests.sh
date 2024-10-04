#!/bin/bash

echo "===================="
echo "WhisperNet Tests"
echo "===================="

echo "Running setup script:"
source install.sh

# Delete the users.db file
echo "Deleting users.db"
rm ./app/instance/users.db

# Nuke old logs
echo "Nuking old logs..."
rm ./app/whispernet.log
rm ./whispernet.log
rm ./audit.*
#echo "Starting Redis"
#redis-server --loadmodule /home/ryan/librejson.so &

echo "Clearing redis"
redis-cli FLUSHALL

# Start the server in the background
echo "Starting Server..."
python3 ./app/whispernet.py &


# Capture the server's PID
SERVER_PID=$!
echo "Server started with PID $SERVER_PID"

# Allow some time for the server to start
sleep 5



# Run the tests
echo "Running tests..."
python3 ../development/tests/user_auth.py
python3 ../development/tests/simple_http.py
python3 ../development/tests/stats.py
python3 ../development/tests/ftp_test.py
python3 ../development/tests/docker.py


#python3 development/tests/client_load_test.py
#python3 development/tests/sequential_client_load_test.py
#python3 development/tests/looping_clients.py

#keep alive
#sleep 1000000000 

# Kill the server after the tests
echo "Killing server with PID $SERVER_PID"
kill $SERVER_PID

# Ensure the server process is terminated
wait $SERVER_PID 2>/dev/null

echo "Server stopped."


