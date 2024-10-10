# file name: buildenv_target_arch

#docker build --build-arg BINARY_NAME=my_custom_binary -t my-image .
ARG BINARY_NAME=default_name

# Start from a minimal Debian image
FROM debian:buster-slim

# SO. Apparenty each FROM command magically makes all previous ARG's go bye bye. 
# As such, we need to redeclare this arg. F#CKING kill me cuz this took way too long to figure out
# https://stackoverflow.com/questions/44438637/arg-substitution-in-run-command-not-working-for-dockerfile
ARG BINARY_NAME

# Install dependencies for cross-compilation and Rust
RUN apt-get update && \
    apt-get install -y \
    gcc-mingw-w64 \
    pkg-config \
    libssl-dev \
    curl \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Rust without prompts (-y flag)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
RUN echo "Rust Install"

RUN apt-get install gcc-mingw-w64
#curl https://sh.rustup.rs -sSf | sh -s -- -y

# Automatically source the Rust environment
ENV PATH="/root/.cargo/bin:${PATH}"

# Add the Windows target for cross-compilation
RUN rustup target add x86_64-pc-windows-gnu

# Set the working directory inside the container
WORKDIR /usr/src/myapp

# Copy your source code to the container
COPY ./agents/windows/dropper .

# Build the Rust application for Windows
RUN cargo build --release --target x86_64-pc-windows-gnu

# Create a directory to store the compiled binary
RUN mkdir /output

# List the files in the target directory for verification
RUN ls -lsa target/x86_64-pc-windows-gnu/release

RUN echo "Copying file to output with name: $BINARY_NAME"

# Copy the compiled binary to the /output directory in the container for volume sharing

# option w bash
#RUN /bin/bash -c "cp target/x86_64-pc-windows-gnu/release/*.exe /output/$BINARY_NAME"

# option raw
RUN cp target/x86_64-pc-windows-gnu/release/*.exe /output/${BINARY_NAME}

RUN ls -lsa /output/

