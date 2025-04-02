# WebSocket (Socket.IO) Technical Documentation

## Overview
- **Library:** Socket.IO
- **Primary Namespace:** `/shell`
- **Room Strategy:** Clients join rooms named after their agent IDs.

## Namespace: `/shell`
---
- All shell-related real-time events occur under this namespace.
- Clients must send a `join` event with their agent ID to be added to a room.

## Events

### connect
- **Triggered When:** A client connects to `/shell`.
- **Server Actions:**
  - Emit `local_notif` with `"Connection Established"`.
  - Request agent ID by emitting `local_notif`: `"Please send your agent id to join a room."`

### ping
- **Purpose:** Measure round-trip latency.
- **Client Payload Example:** `{ "time": 1623847200 }`
- **Server Action:** Echo back the payload immediately.

### join
- **Purpose:** Add client to a room.
- **Client Payload:** `{ "agent_id": "abc-123" }`
- **Server Actions:**
  - Validate and call `join_room(agent_id)`.
  - Emit `local_notif` to the room confirming join: `"Joined room abc-123"`.

### response
- **Purpose:** Transmit command responses.
- **Client Payload:**
  ```json
  {
    "agent_uuid": "abc-123",
    "command_id": "cmd-456",
    "data": "command output"
  }
  ```
- **Server Actions:**
  - Process/log the response.
  - Emit a `local_notif` to the room (using the agent ID) with a confirmation message.

### local_notif
- **Purpose:** Send status updates and notifications, to the current room.
- **Payload:** A simple string message (e.g., `"Joined room abc-123"`).

### global_notif
- **Purpose:** Send status updates and notifications, to every client connected to the websocket.
- **Payload:** A simple string message (e.g., `"Joined room abc-123"`).

### disconnect
- **Triggered When:** A client disconnects.
- **Server Action:** Log the disconnection.

## Rooms
- **Assignment:** Clients join a room based on their `agent_id`.
- **Emitting:** Use the `room` parameter in `emit` to target only that room.
  
**Example:**
```python
# Client joins its room:
ws.emit("join", {"agent_id": "1234-1234-1234-1234"}, namespace="/shell")

# Server emits a response to that room:
ws.emit("response",
        {"agent_uuid": "1234-1234-1234-1234", "command_id": "5555-555-5555-5555", "data": "somedata"},
        namespace="/shell", room="1234-1234-1234-1234")
```

