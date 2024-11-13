# Use Debian Buster as the base image
FROM debian:buster-slim

# Install dependencies for cross-compilation and Rust
RUN apt-get update && \
    apt-get install -y \
    gcc-mingw-w64 \
    pkg-config \
    libssl-dev \
    curl \
    build-essential \
    cmake && \
    rm -rf /var/lib/apt/lists/*

# Install Rust without prompts (-y flag)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Add the Windows target for cross-compilation
RUN rustup target add i686-pc-windows-gnu x86_64-pc-windows-gnu

# Set the working directory inside the container
WORKDIR /usr/src/myapp

# Copy the watch script into the container, which will wait for the code to be copied in before running
COPY ./_docker/dockerfiles/watch_and_run.sh /usr/local/bin/watch_and_run.sh

# create output dir
RUN mkdir /output/

# Make the script executable
RUN chmod +x /usr/local/bin/watch_and_run.sh

# Set the entrypoint to the watch script
ENTRYPOINT ["/usr/local/bin/watch_and_run.sh"]
