# FormJ

## Todo:
- [ ] Create fomr_j test plugin, work in from network side/validate implementation
- [ ] create a generic test for this with correct keys, wrong keys, bad format, etc.


FormJ - Short for Format Json. This is (currently the only) one of the communication formats developed with Whispernet. 

These protocols are designed to work with any transportation channel/protocol, HTTP, DNS, ICMP, basically whatever you can fit it into. 

Currently, a form of FormJ is used to communicate between items in WhisperNet. 

(opt add: It's also the main communication format used in the HTTP C2 Plugin)

## Basic Structure

```json
{
    "data": {},
    "error": {},
    "message": "SomeMessage",
    "rid": "489d3491-c950-4cb8-b485-7dfb1f1aa223",
    "status": 200,
    "timestamp": 1234567890
}
```

The FormJ structure consits of a few elements.

#### data:

The `data` key can include multiple data types, which are JSON subkeys. These are called `Sync Keys`. Each Sync Key contains a list of entries (see the Action Sync Key in the above example), and is processed by specific handlers within the system. ~~See [Sync Key Types](#sync-key-types) for current Sync Keys.~~

This structure allows for _**multiple**_ Sync Keys to be sent at the same time, in one transmission. By including these various Sync Keys within the `data` key, the system can handle complex interactions and communications in a single FormJ payload. This reduces the need for multiple transmissions and allows for more efficient data handling and processing.

Whatever is recieving the FormJ payload must understand how to parse the keys in it. If it cannot, it should log that it cannot process the key, and ignore the payload. The method used for parsing the sync keys, are `Sync Handlers`. Each sync handler knows how to handle one specific key. 

```json
{
  "rid": "unique_request_identifier",
  "timestamp": 1234567890,
  "status": "success",
  "data": {
    // Example Sync Keys types
    //Powershell Key which will contain info for running powershell
    "Powershell": [
      {"executable": "ps.exe","command": "net user /domain add bob", "id": 1234},
      {"executable": "ps.exe","command": "net group /add Domain Admins Bob", "id": 1235}
    ],
    //Some other Sync Key, that does Some Other thing
    "SomeSync": [
      {"somedata": "somedata"},
      {"somedata": "somedata"}
    ]
  },
  "error": {"message": null, "aid": [null, null], "rid": null}
}
```


#### error
The error field that holds errors

#### message
A message to go along with the message

#### status
(HTTP only currently) status code to go along with the message

#### timestamp
UNIX timestamp for message