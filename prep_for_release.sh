#!/bin/bash

echo "===================="
echo "Release Prep"
echo "===================="

echo WARNING! This will delete all Database, log, and Env files. Waiting for 10 seconds, press CTRL C to cancel.

sleep 10

# Find and delete all .db files
echo "Deleting all .db files"
find . -type f -name "*.db" -exec rm -f {} \;

# Find and delete all .log files
echo "Nuking all .log files..."
find . -type f -name "*.log" -exec rm -f {} \;

echo "Nuking .env files..."
find . -type f -name "*.env" -exec rm -f {} \;

echo "Should be good to go!"
