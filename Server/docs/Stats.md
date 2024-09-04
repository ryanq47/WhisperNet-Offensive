# Stats

A stats plugin


## /plugins:
Holds current plugin data/active services, this is (or will be) used to display info about the server on the web client. 

```
{
  "data": {
    "ActiveServices": [
      {
        "info": "FTP Server",
        "ip": "0.0.0.0",
        "pk": "01J6ZNCMBSXESS1VY5ZZJJKQ18",
        "port": 21,
        "sid": "f704b7fb-0c1f-4491-b46d-b3b9795e0245",
        "timestamp": "1725491990"
      }
    ]
  },
  "message": "",
  "rid": "24bab96f-770a-486c-8be1-aedc918c22cf",
  "status": 200,
  "timestamp": 1725491992
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