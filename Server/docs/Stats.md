# Stats

A stats plugin


## /services:
Holds current plugin data/active services, this is (or will be) used to display info about the server on the web client. 

```
{
  "data": {
    "ActiveServices": [
      {
        "info": "FTP Server",
        "ip": "0.0.0.0",
        "name": "FTP Server",
        "pk": "01J722MDA2QAP48MSKFBR66A8P",
        "port": 21,
        "sid": "18cf528d-fff4-41f5-859a-a7991bfa18c6",
        "timestamp": "1725572986"
      }
    ]
  },
  "message": "",
  "rid": "9f620b26-c048-45b9-a7b4-a178d2fd10fa",
  "status": 200,
  "timestamp": 1725572987
}
```

## /clients
Sends out a FormJ message containing all the clients currently on the server.

Ex:

```
{
  "data": {
    "client:modules.redis_models.Client:02637f18-14f4-4c3d-a4cf-ee95e6a33037": {
      "checkin": "1724653632",
      "client_id": "02637f18-14f4-4c3d-a4cf-ee95e6a33037",
      "pk": "01J66NVYZQDAA9R671YBCD5PSX",
      "type": "simple-http"
    },
    "client:modules.redis_models.Client:0864c139-134f-4fa0-b68a-61ffb9b8591e": {
      "checkin": "1724653631",
      "client_id": "0864c139-134f-4fa0-b68a-61ffb9b8591e",
      "pk": "01J66NVYDVCN203BEVZJQ67FGJ",
      "type": "simple-http"
    },
  "message": "",
  "rid": "294ed3b7-2b6a-4f2c-b673-24c5a3361988",
  "status": 200,
  "timestamp": 1724653653
}

```