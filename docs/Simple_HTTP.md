# Simple HTTP

A simple HTTP C2 protocol. Designed to be stupid simple, no tricks, etc, just straight up HTTP. More of a testbed for the rest of the framework. Uses FormJ to communicate


## Endpoints

#### `get/{clientname}`

Gets the next command

#### `post/{clientname}`

Post the resulting command back


## Backend
Client commands + Queue held in Redis.

NO threatmodeling/Client modeling w neo4j yet. That will come later

## Comms:

Beacon Style:
1. Client reaches out to `get/{clientname}`
    - Server gives payload/command
2. Client runs command/actions
    - Client sleeps for specified time
3. Client posts command back to `post/{clientname}`
jump to step 1