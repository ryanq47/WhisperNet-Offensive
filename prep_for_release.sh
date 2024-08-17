#!/bin/bash

echo "===================="
echo "Release Prep"
echo "===================="

# Find and delete all .db files
echo "Deleting all .db files"
find . -type f -name "*.db" -exec rm -f {} \;

# Find and delete all .log files
echo "Nuking all .log files..."
find . -type f -name "*.log" -exec rm -f {} \;

echo "Should be good to go!"
