# Whispernet Redis Setup Guide

Whispernet requires Redis for fast in-memory operations, along with RedisJSON for handling JSON objects. If you're not on Ubuntu/Debian/Kali, or are running into issues with Redis, follow these steps to manually install and configure Redis and RedisJSON.

If you ARE on Ubuntu/Debian/Kali, it should just all work, as I've included the `lib/librejson.so` object in the project. 


HEYYYYYYYYYYY
- Once laptop re installed, use redis-stack-server in docker container. 

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

By default, the `librejson.so` is included with the project. However, if you are on a different architecture, etc, you may need to build it manually. If you're on Ubuntu/Debian/Kali, don't worry about it.

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


## 3. Start/Use Redis with RedisJSON Module

For whispernet to successfully load this .so, it must be in the `lib` folder of the project, so please copy it there. `redis-server` is automatically run on startup from `app/start.sh`


```
├── README.md
├── app
├── development
├── docs
├── lib
│   └── librejson.so << HERE
├── prep_for_release.sh
├── requirements.txt
├── run_tests.sh
└── whispernet.log

```

---

