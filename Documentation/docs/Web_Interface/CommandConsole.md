# Command Console

Command console is the universal command interface for interacting with a client. Some inspiration is borrowed from CrowdStrike's RTR console, so if you've ever used that, this should feel farmiliar.

## Usage:

![type:video](https://www.youtube.com/embed/LXb3EKWsInQ)


## Technical
The "console" is simply a page that makes API calls to the server, and presents the results to mimic the appearance of a real TTY.


### What happens when you open the console:
Each console is initiated at `/command/<client-id>`, where `client-id` represents the client's UUID.

Each console instance is stateless, meaning a new class instance is created every time you open it. As a result, command history is lost upon refreshing the page. However, the command history is stored server-side in audit logs. In the future, there may be a log endpoint available on the web client for retrieving command history.


### What happens when you hit the `run` button

When you press "run," several steps take place:

1. **Parsing the Command**  
   The entered command is parsed.

    - Note:  If the command is `help`, a help menu is returned. This menu is constructed from the "help" method within the FormJ keys, *not* from the server.  
   Why this matters: Some commands may appear in the help menu but may not be supported by the client. This is a flaw, but it works fine for now.

2. **Creating a FormJ Message**  
   From the parsed command, a Sync Key is created. That key is then loaded into a FormJ message (in the `data` field). The FormJ message is sent to the server and queued for the client.  
   Example: `http://server/command/<client-id>`

3. **Receiving the Response**  
   Immediately after sending the message, a timer is initiated. This timer checks the "response" URL of the command (e.g., `http://server/response/<rid>`) every second until a valid response is received. Once the message is successfully retrieved, the timer is canceled, stopping further requests to that URL.

4. **Displaying the Response**  
   The response is in FormJ format. Responses contain a `blob` key, used to transfer blobs of data. The `data` field from each blob entry is displayed on the screen in the console.


Example response from server:
```
{
  "data": {
    "blob": [
      {
        "encoding": "text",
        "data": "aaaaaaaahhhhh",
        "size": "1234"
      },
      {
        "encoding": "text",
        "data": "ahhhhhhhhhhhhh",
        "size": "1234"
      }
    ]
  },
  "message": "",
  "rid": "12345-56789-09187",
  "status": 200,
  "timestamp": 1724730258
}

```