# FormJ

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
data feild blah blah subkeys


#### error
error feild blah blah

#### message
A message to go along with the message

#### status
(HTTP only currently) status code to go along with the message

#### timestamp
UNIX timestamp for message