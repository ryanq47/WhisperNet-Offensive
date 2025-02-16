# HTTP


Agent communication over HTTP BreakDown


## Important Data Structures:

Receiving Commands:


C Version:
```
typedef struct {
    char *command_id;   // Command ID: Vital for tracking the commands accurately
    char* command;      // the command (ex: shell)
    char* args;         // Arguments to accompany the command

} JsonDataCommand;

```

Returning Output:

```
typedef struct {
    char id[37];        // AgentID (max 36 chars + null terminator), for identifying where the data is coming from
    char *data;         // Data, contains the output of the command/data that the command generates
    char *command_id;   // Command ID: Vital for tracking the commands accurately
} JsonData;

```

## Flow of Agent:

### HTTP (High Level):
1. **Loop Start:**  
   The agent runs continuously in a loop.

2. **GET Command:**  
   It makes a GET request to the server to retrieve a JSON command.

3. **Command Parsing:**  
   The received JSON is parsed into a `JsonDataCommand` structure. If valid, the agent creates a new `JsonData` response structure, initializes it (e.g., with a UUID), and passes it along.

4. **Command Execution:**  
   The agent executes the command by calling a parsing function that fills the response structure with any output data.

5. **POST Response:**  
   The filled response is encoded back into JSON and sent to the server via a POST request.
    
    > Upon successful post request, this data is stored in redis, and can now be retrieved by the user/etc.

6. **Sleep and Repeat:**  
   After cleaning up allocated memory, the agent sleeps for a set period before starting the next loop iteration.

This concise flow captures the core steps the agent follows during its execution cycle.

### HTTP (Technical)
1. **(On execution) A loop is started.**

    The agent continuously runs a loop to check for new commands from the server.

2. **Agent makes a GET request to the server.**

    The agent calls the function get_command_data(), which sends a GET request to the server and retrieves a command.

3. **Server responds with a JsonDataCommand JSON data structure.**

    The server’s response is parsed into a JsonDataCommand structure. This structure contains fields such as command, command_id, and args.

4. **Agent parses the command and prepares a response structure.**

    The agent verifies that command_struct.command is valid. It then prints the decoded command and creates a new JsonData structure (named response_struct).

    A fixed UUID is assigned to response_struct->id.
    The response_struct->data field is initialized to NULL.
    This structure will later hold the output of the executed command.

5. **Command execution and population of the response.**

    The agent processes the command by calling:


```
parse_command(command_struct.command, command_struct.args, response_struct);
```
    
This function executes the desired command and fills in response_struct with any output data.

6. **Agent sends a POST request with the JSON-encoded response.**

    The agent converts the response structure into a JSON string using:

```
char* encoded_json_response = encode_json(response_struct->id, response_struct->data, command_struct.command_id);
```
Then, it sends this JSON data back to the server via a POST request by calling:


```
post_data(encoded_json_response);
```

7. **Memory cleanup and sleep before the next iteration.**

    After sending the response, the agent frees the allocated memory for the command and response structures. Finally, it sleeps (using WhisperSleep(1000 * 60)) for 60 seconds before looping back to step 1.

