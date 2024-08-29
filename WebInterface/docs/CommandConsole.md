# CommandConsole

Command console is a universal command interface. 


## Technical
it's just an API client basically

spawns at `/command/<client-name>`

Stateless, aka a new class instance is spawned each time you open it, and as such, you don't get any command history if you refresh the page. (Command history *is* stored server side in the audit logs). Maybe in the future there will be a log endpoint on the web client

## What happens when you hit run
When hitting run, a few things happens

1. Parsing 

    The entered command is parsed

    1a. If the command is `help`, a help menu is returned. The help menu is constructed from the "help" method in the FormJ keys, *NOT* from the server. Why this matters: Some commands may be listed in the help menu, they may not be supported by the client. Yes this is a flaw, but it works fine for now.



2. Form J Message 

    From that parsing, a Sync Key is created. That key then gets loaded into a FormJ message (in the `data` field). That FormJ message is then sent to the sever to be queued for the client. ex: `http://server/command/<client-id>`

3. Getting response 

    Right after sending, a timer is created, that checks the "response" url of the command sent(ex: `http://server/response/<rid>`) every second until a valid respnose is received. 
    Upon a successful message retrieveal, the timer is deleted, and as such, the no more requests are made to that url. 

4. Display response

    THe response is in a FormJ format. Responses also contain the `blob` key, which is just for transfering blobs of data. the `data` field from each blob entry is then displayed on screen in the console.

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