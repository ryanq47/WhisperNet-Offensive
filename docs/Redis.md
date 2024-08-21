# Whispernet Redis Setup Guide

Whispernet requires Redis for fast in-memory operations, along with RedisJSON for handling JSON objects. Follow these steps to manually install and configure Redis and RedisJSON.

## 1. Install Redis

To install Redis, run the following command:

```bash
sudo apt-get install redis-server
```

## 2. Install RedisJSON

### Step 1: Install Rust

RedisJSON requires Rust. Install it by running:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

> **Note:** After installation, either remember the path of the installed Cargo binary (usually `~/.cargo/bin/cargo`) or add it to your PATH.

### Step 2: Download RedisJSON

Download the latest release of RedisJSON from the official GitHub repository:

```bash
wget https://github.com/RedisJSON/RedisJSON/archive/refs/heads/master.zip
unzip RedisJSON-master.zip
cd RedisJSON-master
```

### Step 3: Build RedisJSON

In the RedisJSON code directory, run the following command to build the module:

```bash
cargo build --release
```

Upon successful build, the module will be located at `target/release/librejson.so`.

> **Note:** You can move `librejson.so` to any location, but remember the full path for later use.

## 3. Start Redis with RedisJSON Module

You can start Redis and load the RedisJSON module using the following command:

```bash
redis-server --loadmodule <path_to_librejson.so>
```

Replace `<path_to_librejson.so>` with the full path to the `librejson.so` file.

### Alternative: Edit Redis Startup Configuration

To have Redis load the RedisJSON module automatically on startup, edit the startup file:

1. Open the Redis service file in a text editor:

   ```bash
   sudo nano /usr/lib/systemd/system/redis-server.service
   ```

2. Modify the `ExecStart` line to include the RedisJSON module:

   ```bash
   ExecStart=/usr/bin/redis-server /etc/redis/redis.conf --supervised systemd --daemonize no --loadmodule <full_path_to_librejson.so>
   ```

   Replace `<full_path_to_librejson.so>` with the absolute path to the `librejson.so` file.

3. Save the file and restart the Redis service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart redis-server
   ```

---

