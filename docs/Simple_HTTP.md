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
        - need to find way to not overwrite already existing key?
        - a "request" prefix, and a "response" prefix?
            `request:plugins.simple_http.modules.redis_models.FormJModel:12345-56789-09187`
            `response:plugins.simple_http.modules.redis_models.FormJModel:12345-56789-09187`
            - Dynamically setting this with a classmethod in redis_models.FormJModel. Only do this if the function is saving to redis

    - jump to step 1

#### Request Vs Response

Request ID's are used consistenlty through ..., basically, when a command is queued, it has a rid. That RID is reused when sending to the client, and the client sends it's response back with that same RID. This is all for easyish tracking purposes. 

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
    Failed response: Sleep?

    Error on server side: Send sleep?

Tracking REsponses:
    Keep the same RID between request/response? how else to track the response

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
- Biggest failure point is the FileRotateHandler, especially when trying to switch files.
- Command is pretty slow on response times too

Output from a test: 
```
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Endpoint ┃ Status  ┃   Count   ┃ Avg. Response Time (ms) ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ get      │ Success │ 948/1000  │          9.88           │
│ get      │ Failure │  52/1000  │                         │
│ post     │ Success │ 1000/1000 │          7.01           │
│ post     │ Failure │  0/1000   │                         │
│ command  │ Success │ 797/1000  │         384.49          │
│ command  │ Failure │ 203/1000  │                         │
└──────────┴─────────┴───────────┴─────────────────────────┘


```