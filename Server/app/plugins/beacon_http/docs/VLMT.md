### Simplified RFC: Variable-Length Message Transmission Protocol (VLMT)

---

#### Title: **Variable-Length Message Transmission Protocol (VLMT)**  
**Author:** Ryan Kleffman  
**Status:** Draft  
**Date:** November 18, 2024  

---

### 1. Introduction

VLMT defines a simple way to send variable-length data over socket connections. The protocol uses an 8-byte prefix to indicate the size of the message, followed by the actual message payload. This ensures efficient, reliable communication.

---

### 2. Protocol Specification

#### 2.1. Message Format
Each message consists of:
1. **Length Prefix**: An 8-byte binary value (unsigned 64-bit integer) indicating the size of the payload.
2. **Payload**: The actual message data, in bytes.

| **Length Prefix** (8 bytes) | **Payload** (variable) |
|-----------------------------|------------------------|
| Unsigned 64-bit integer     | Message data          |

---

### 3. Sender Behavior
1. Calculate the length of the message payload in bytes.
2. Pack the length as an 8-byte value using network byte order.
3. Send the packed length, followed by the message payload.

#### Example (Python):
```python
import struct
sock.sendall(struct.pack('!Q', len(payload)) + payload)
```

---

### 4. Receiver Behavior
1. Read exactly 8 bytes to determine the payload size.
2. Use the size to read the exact amount of message data from the socket.
3. Process the received data.

#### Example (Python):
```python
length = struct.unpack('!Q', sock.recv(8))[0]
payload = sock.recv(length)
```

---

### 5. Best Practices
- **Input Validation**: Reject excessive payload sizes to prevent denial-of-service attacks.
- **Encryption**: Use TLS or similar to secure communication.
- **Timeouts**: Set socket timeouts to avoid blocking indefinitely on partial reads.

---

### 6. Use Cases
- **File Transfer**: Sending files with variable sizes.
- **Client-Server Messaging**: Communication in chat applications or telemetry systems.
- **Command-and-Control (C2)**: Exchanging variable-length commands stealthily.

---

### 7. Example
For the message `b'Hello, server!'` (13 bytes):
1. Sender sends:
   ```
   Length Prefix: b'\x00\x00\x00\x00\x00\x00\x00\x0D'
   Payload: b'Hello, server!'
   ```
2. Receiver reads:
   - Prefix: `13` (from binary).
   - Payload: `b'Hello, server!'`.

---

### 8. Advantages
- Simple and efficient.
- Handles messages of any size (up to 16 exabytes).
- Compatible with binary data.

---

### 9. Conclusion

VLMT provides a straightforward and reliable way to transmit variable-length data. By using an 8-byte prefix, it eliminates ambiguity in message parsing while supporting both small and extremely large payloads.

--- 

Let me know if you want further edits!