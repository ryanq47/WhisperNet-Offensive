# **HTTP Communication Overview**  

One of (and currently the only) communication methods betwen the Agent and C2 server, is `HTTP`. The interaction follows a structured request-response cycle, ensuring efficient and reliable command execution. 

Overall, it's a pretty common communication method, nothing too fancy.

Quick note, any Agent that can speak the JSON spec here, can communicate with the server.

---

## **Communication Flow** 
```
           ┌───────────────────────────────────────────┐
           │                 Agent                    │
           └───────────────────────────┬──────────────┘
                                       │ 1) GET /get/<agent_uuid>
                                       │    (Requests a new command)
                                       ▼
           ┌───────────────────────────────────────────┐
           │                C2 Server                 │
           │  (Receives GET request, returns JSON)    │
           └───────────────────────────┬──────────────┘
                                       │ JSON response example:
                                       │   {
                                       │     "command_id": "550e8400-e29b-...",
                                       │     "command": "shell",
                                       │     "args": "whoami"
                                       │   }
                                       │ 
                                       ▼
           ┌───────────────────────────────────────────┐
           │                 Agent                    │ 2) command gets run
           │  (Executes the command locally)          │
           └───────────────────────────┬──────────────┘
                                       │ 3) POST /post/<agent_uuid>
                                       │    (Sends execution results)
                                       ▼
           ┌───────────────────────────────────────────┐
           │                C2 Server                 │
           │  (Receives POST, stores command output)  │
           └───────────────────────────┬──────────────┘
                                       │ Example POST body:
                                       │  {
                                       │    "id": "a1b2c3d4-...",
                                       │    "data": "desktop-123456\\Bob",
                                       │    "command_id": "550e8400-e29b-..."
                                       │  }
                                       │ 4) Server stores this data
                                       ▼
           ┌───────────────────────────────────────────┐ 5) Agent sleeps
           │                 Agent                    │
           │ (Sleeps, then repeats the cycle)         │
           └───────────────────────────────────────────┘


``` 

1. **Agent Requests a Command (GET Request)**  
   
    - The Agent sends an **HTTP GET request** to the C2 server, requesting a new command.  
    - The server responds with a structured **JSON object** containing the command and its parameters.  

3. **Agent Executes the Command**  
   
    - The Agent processes the received instruction.  
    - It executes the requested task and captures any generated output.  

3. **Agent Sends Execution Results (POST Request)**  
   
    - The Agent formats the execution result as **JSON**.  
    - It sends the **HTTP POST request** back to the C2 server with the results.  

4. **Server Stores the Response**  
   
    - The C2 server processes and stores the received execution results.  
    - These results can be retrieved later for review or further actions.  

5. **Agent Sleeps & Repeats**  
   
    - After completing the cycle, the Agent sleeps for a set duration.  
    - It then repeats the process by requesting a new command.  


---

## **HTTP Request and Response Structure**  

### **Fetching Commands (GET Request)**  
**Endpoint:**  
```
GET /get/<agent_uuid>
```
The Agent requests a new command from the C2 server by calling the `/get/<agent_uuid>` endpoint.

**Example Response (JSON Command Object):**  
```json
{
    "command_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "shell",
    "args": "whoami"
}
```

**JSON Field Descriptions:**  

| Field         | Type   | Description                                        |
|--------------|--------|-----------------------------------------------------|
| `command_id` | String | Unique identifier for tracking the command.         |
| `command`    | String | The action the Agent should perform (e.g., `shell`) |
| `args`       | String | Optional arguments associated with the command.     |

---

### **Sending Execution Results (POST Request)**  
**Endpoint:**  
```
POST /post/<agent_uuid>
```
The agent sends execution results to the C2 by calling the `/post/<agent_uuid>` endpoint.

**Example POST Request (JSON Response Object):**  

```json
{
    "id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
    "data": "desktop-123456\Bob",
    "command_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**JSON Field Descriptions:**  

| Field        | Type   | Description                                      |
|-------------|--------|--------------------------------------------------|
| `id`        | String | The unique **Agent ID**.                         |
| `data`      | String | The **command output** generated by execution.   |
| `command_id`| String | Unique identifier that **matches the request**.  |

---


## **Recap**  

So, in a nutshell

- The Agent retrieves commands via HTTP GET (`/get/<agent_uuid>`).  
- Executes received commands and captures output.  
- Sends execution results via HTTP POST (`/post/<agent_uuid>`).  

And does this all with structured JSON data for requests and responses.  
