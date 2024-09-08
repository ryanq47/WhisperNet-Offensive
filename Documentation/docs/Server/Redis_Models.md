# Redis Models

Redis models available to the entire program, not just plugin specific


## Client model
THe client model is meant to be a standard way to store lightdetails on a client, such as checkin times, and type. 
Basically, when a client checks in, either a key is created, or updated, based on it's ID with the follwoing information:

`client_id`: ID of the client

`type`: Client type, such as `simple_http`. 

`checkin`: last checkin time, in unix time

```
127.0.0.1:6379> hgetall client:modules.redis_models.Client:d94670d6-bc49-4ed7-8f26-fd8470e77fa2
1) "pk"
2) "01J66NVYW5F1RKEJ5P164XHXWP"
3) "client_id"
4) "d94670d6-bc49-4ed7-8f26-fd8470e77fa2"
5) "type"
6) "simple-http"
7) "checkin"
8) "1724653632"
```

Together, all these keys make up the contents of the `/clients` endpoint, which contain all the clients:

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