# Simple HTTP

A simple HTTP C2 protocol. Designed to be stupid simple, no tricks, etc, just straight up HTTP. More of a testbed for the rest of the framework. Uses FormJ to communicate


## Endpoints

#### `get/<client-id>`

Gets the next command for the client.

#### `post/<client-id>`

For clients to post the results of the command back to.

Takes formJ message.

#### `command/<client-id>`

Queue a command to the client. 

Takes a formJ message with appropriate sync keys for commands.

Example:
```
{
    "rid": "12345-56789-09187",
    "message": "somemessage",
    "timestamp": 1234567890,
    "status": 200,
    "data": {
        "Powershell": [
            {
                "executable": "ps.exe",
                "command": "net user /domain add bob",
                "id": 1234
            },
            {
                "executable": "ps.exe",
                "command": "net group /add Domain Admins Bob",
                "id": 1235
            }
        ]
    }
}
```
#### `response/<request-id>`

For lookign up specific request ID responses.

Pass in a request-id, and it'll pass back a formJ message with the response from the client if it exsits


## Backend
Client commands + Queue held in Redis.

NO threatmodeling/Client modeling w neo4j yet. That will come later

## Comms:

Beacon Style:

0. First/Any time - A command is queued for a client at `command/<client-id>`
    - this is stored with a specific RID

1. Client reaches out to `get/<client-id>`
    - Server gives payload/command
    - server gives this payload with SAME rid
        - makes managing easier

2. Client runs command/actions
    - Client sleeps for specified time

3. Client posts command back to `post/<client-id>`
    - also with SAME rid.
    - jump to step 1

#### Request Vs Response

Request ID's are used to track messages, basically, when a command is queued, it has a rid. That RID is reused when sending to the client, and the client sends it's response back with that same RID. This is all for easyish tracking purposes. 

In order to differentiate these keys in redis, a `request` or `response` prefix is added to each key. 

Ex: 

Request Key Name
```
request:plugins.simple_http.modules.redis_models.FormJModel:12345-56789-09187
```

Response Key Name
```
response:plugins.simple_http.modules.redis_models.FormJModel:12345-56789-09187
```

To simplify the code side of these, only one model exists for mapping requests/responses to redis. As such, the prefix is set deynamically:

```
FormJModel.set_prefix("request")

```

Downsides:

There's some downsides to this, if a bug exists/a prefix doesn't get set properly, some weird things could happen, such as responses getting sent to clients, instead of requests. 

This may change going forward, but for now works.

#### Other Ideas/EdgeCase thoughts:

Sleep/Error behavior: 
    - Failed response: Sleep?
    - Error on server side: Send sleep?

Tracking Responses:
    - Keep the same RID between request/response? how else to track the response

Big responses:
    - If exceed the size or whatever, and need to chunk... do that on the HTTP side, not on the redis side. TLDR: get the whole msg, then write to redis


## Redis setup
Details related to the redis setup in the simple_http plugin

### Keys:
---
#### Command Key
`:plugins.simple_http.modules.redis_models.FormJModel:12345-56789-09187`

The command key holds the command receieved for the client.

Example contents of this key, which is just a condensed FormJ message.  

This should be stored in a much more efficent way than just the JSON string, I used json.get in redis-cli to view the contents of it, which returned the string.

```
"{\"pk\":\"01J5YET9G4Z7Q9FE8XKT9MTHR5\",\"rid\":\"12345-56789-09187\",\"data\":{\"Powershell\":[{\"executable\":\"ps.exe\",\"command\":\"net user /domain add bob\",\"id\":1234},{\"executable\":\"ps.exe\",\"command\":\"net group /add Domain Admins Bob\",\"id\":1235}],\"SomeSync\":[{\"somedata\":\"somedata\"},{\"somedata\":\"somedata\"}]},\"message\":\"somemessage\",\"status\":200,\"timestamp\":1234567890}"
```

You may notice that besides the RID, there's no tracking for which client this command goes to. That's where the FormJQueue comes into play

#### FormJQueue Key
`FormJQueue:1234-5678-0000`: A Queue key, meant to hold the next command to be sent to the client. 

Example contents of this key:

```
127.0.0.1:6379> LRANGE test-client-id 0 -1
1) "12345-56789-00001" # These are the ID's of the next message for the client
2) "12345-56789-00002"
```

Then, when a command is requested, it does alookup with the RID that was popped from the FormJQueue, gets the command, and sends it back to the client.


#### Addtl Notes
The data field for the Command keys in redis do not validate the type(s) of sync keys in said field. TLDR: Any json dict can go into the data field. 

## StressTest Notes:

- [X] Command is pretty slow on response times too
    - fixed, bug with Audit. switched to singleton, which reduced it greatly. Probably was making a new logger each time it was called

- [X] Failing get commands abuot 33% of the time. My guess is that the command is being sent, then being requested too quickly/not in redis in time?

    - It was the test. it was sending requests out of order, so as such, some queue's didn't have anything in them. Good news: this edgecase has been handled.

Output from a test: 
```
             Response Summary for 100 Clients             
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Endpoint ┃ Status  ┃  Count  ┃ Avg. Response Time (ms) ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ get      │ Success │ 100/100 │          3.25           │
│ get      │ Failure │  0/100  │                         │
│ post     │ Success │ 100/100 │          3.00           │
│ post     │ Failure │  0/100  │                         │
│ command  │ Success │ 100/100 │          3.64           │
│ command  │ Failure │  0/100  │                         │
└──────────┴─────────┴─────────┴─────────────────────────┘
```