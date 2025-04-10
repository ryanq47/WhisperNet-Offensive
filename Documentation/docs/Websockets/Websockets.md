

# WebSocket (Socket.IO) Technical Documentation
---

## Overview
- **Library:** Socket.IO
- **Primary Namespace:** `/shell`
- **Room Strategy:** Clients join rooms based on their agent IDs. When joining, clients must send a `join` event with the agent ID, and all subsequent events can be targeted by specifying the room.

---

## Namespace: `/shell`

All shell-related real-time events occur under this namespace. When clients connect to `/shell`, the server instructs them to provide their agent ID so they can be placed in the matching room.

---

## Events

### connect
- **Triggered When:** A client connects to `/shell`.
- **Server Actions:**
  - Log the connection.
  - Emit a `local_notif` message with **"Connection Established"**.
  - Immediately request the agent ID by emitting another `local_notif`: **"Please send your agent id to join a room."**

---

### ping
- **Purpose:** Measure round-trip latency.
- **Client Payload Example:**  
  ```json
  { "time": 1623847200 }
  ```
- **Server Action:**  
  Immediately echo back the exact payload so that the client can calculate latency.

---

### join
- **Purpose:** Add the client to a room named after its agent ID.
- **Client Payload:**  
  ```json
  { "agent_id": "abc-123" }
  ```
- **Server Actions:**
  - Validate the provided `agent_id`.
  - Call `join_room(agent_id)` to add the client to the matching room.
  - Emit a `local_notif` to the room, confirming the join, e.g., **"Joined room abc-123"**.

---

### display_on_terminal
- **Purpose:** Display output or notifications directly on an agent’s terminal.
- **Client Payload:**  
  ```json
  {
    "agent_id": "abc-123",
    "data": "Data to display"
  }
  ```
- **Server Actions:**
  - Validate that both `agent_id` and `data` are provided.
  - Emit a `local_notif` to the room (i.e., the specified agent’s room) with the provided data.
  - Logs the reception of the event for debugging purposes.

---

### on_agent_connect
- **Purpose:** Notify that an agent has connected.
- **Client Payload:**  
  ```json
  { "agent_id": "abc-123" }
  ```
- **Server Actions:**
  - Validate that an `agent_id` is provided.
  - Emit the event **`on_agent_connect`** (with the same payload) to the room identified by the agent ID.
  - This can be used to trigger routines or notifications once an agent is confirmed to be online.
- **Trigger**: This is ONLY triggered by listeners, when an agent checks in to get the next command.

---

### on_agent_first_connect
- **Purpose:** A distinct event to signal the very first connection of an agent. 
- **Client Payload:**  
  ```json
  { "agent_id": "abc-123" }
  ```
- **Server Actions:**
  - Validate that an `agent_id` is provided.
  - Emit the **`on_agent_first_connect`** event to the corresponding room.
  - This event helps differentiate between an agent’s first connection and subsequent reconnections.
- **Trigger**: This is ONLY triggered by listeners, on an agents first connect.

---

### on_agent_data
- **Purpose:** Transmit data or command responses from an agent.
- **Client Payload:**  
  ```json
  {
    "agent_id": "abc-123",
    "command_id": "cmd-456",
    "data": "Command response data"
  }
  ```
- **Server Actions:**
  - Validate that `agent_id`, `command_id`, and `data` are provided.
  - Log the received response for debugging or auditing purposes.
  - Emit the **`on_agent_data`** event to the room corresponding to the agent, distributing the response data.

- **Trigger**: This is ONLY triggered by listeners, when an agent posts back data.

---

### local_notif
- **Purpose:** Send status updates and notifications.
- **Payload:** A simple string message (e.g., **"Joined room abc-123"**).
- **Usage:** Can be emitted either during the initial handshake (as seen in `connect` and `join`) or after processing other events.

---

### global_notif
- **Purpose:** Send status updates and notifications to every client connected to the WebSocket.
- **Payload:** A simple string message.
- **Usage:** Useful for broadcast messages that are meant for all agents, regardless of their room.

---

### disconnect
- **Triggered When:** A client disconnects from the `/shell` namespace.
- **Server Actions:**
  - Log the disconnection.
  - Optionally, cleanup any client-specific state if required.

---

## Rooms

Rooms are used to target messages to specific agents. Each client is placed in a room named after its `agent_id`. This strategy allows the server to send events to one or more particular agents without broadcasting to all connected clients.

**Example Usage:**
```python
# Client-side: joining the agent room
ws.emit("join", {"agent_id": "1234-1234-1234-1234"}, namespace="/shell")

# Server-side: emitting a command response to a specific agent
ws.emit(
    "response",
    {"agent_uuid": "1234-1234-1234-1234", "command_id": "5555-555-5555-5555", "data": "somedata"},
    namespace="/shell", 
    room="1234-1234-1234-1234"
)
```

---

## Additional Notes

- **Event Duplication:**  
  While it is acceptable to use the same event name for both incoming and outgoing messages (as seen with some echo or status events), be cautious of potential infinite loops if clients automatically rebroadcast the same event on receipt.

- **Logging:**  
  Each event handler includes logging for debugging purposes. Ensure that your logging system is configured to capture these messages for future reference.

- **Validation:**  
  Each event validates that required fields (such as `agent_id`, `command_id`, etc.) are provided in the payload. Missing data will log an error and may trigger an error notification to the client.

- **Extensibility:**  
  With the addition of specific events like `on_agent_connect` and `on_agent_first_connect`, you can differentiate between initial handshakes and reconnections, providing more granular control over agent behavior.

