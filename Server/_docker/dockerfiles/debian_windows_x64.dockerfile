# file name: buildenv_target_arch
# Start from a minimal Debian image
FROM debian:buster-slim

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
COPY ./agents/dropper/ .

# Build the Rust application for Windows
RUN cargo build --release --target x86_64-pc-windows-gnu

# Create a directory to store the compiled binary
RUN mkdir /output

# List the files in the target directory for verification
RUN ls -lsa target/x86_64-pc-windows-gnu/release

# Copy the compiled binary to the /output directory for volume sharing
RUN cp -r target/x86_64-pc-windows-gnu/release/*.exe /output/

RUN ls -lsa /output/
## Build
#docker build -t my-rust-app -f buildenv_target_arch .

## then run w volume args
#docker run --rm -v $(pwd)/agent:/output my-rust-app



# Copy the compiled binary to /output directory
#RUN cp target/x86_64-pc-windows-gnu/release/myapp /output/

