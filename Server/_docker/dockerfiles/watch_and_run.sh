#!/bin/bash

# Directory to watch for .toml files
WATCH_DIR=${WATCH_DIR:-"/usr/src/myapp/"}  # Default to /usr/src/myapp if not specified
INTERVAL=${INTERVAL:-3}                   # Check every 3 seconds by default
PLATFORM=${PLATFORM:-"x64"}               # Default to x64; options are "x86" or "x64"
BINARY_NAME=${BINARY_NAME:-"default_name"} # Default binary name

LOG_FILE="/output/build_log.txt"
mkdir -p /output  # Ensure the log directory exists

{
    echo "Waiting for a .toml file in $WATCH_DIR to become available..."

    # Loop until a .toml file is found in the specified directory
    while [ -z "$(find "$WATCH_DIR" -type f -name '*.toml')" ]; do
        sleep "$INTERVAL"
    done

    echo "Found .toml file(s) in $WATCH_DIR. Proceeding with setup..."

    ls -lsa "$WATCH_DIR"

    # Determine target based on PLATFORM environment variable
    if [ "$PLATFORM" == "x86" ]; then
        TARGET="i686-pc-windows-gnu"
    elif [ "$PLATFORM" == "x64" ]; then
        TARGET="x86_64-pc-windows-gnu"
    else
        echo "Invalid PLATFORM specified. Use 'x86' or 'x64'."
        exit 1
    fi

    echo "Building for platform: $PLATFORM with target: $TARGET"

    # Run the build command for the specified platform
    cargo build --release --target "$TARGET"

    # Copy the built binary to the output directory with the specified name
    cp target/$TARGET/release/*.exe /output/${BINARY_NAME}.exe

    ls -lsa /output

    echo "Build complete. Output located in /output/${BINARY_NAME}.exe"
} | tee -a "$LOG_FILE"

#sleep 360