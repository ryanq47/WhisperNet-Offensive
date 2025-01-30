## Redesign/Adjust:



2 classes;

 - Listener class (VLMT)
    - Spawned once per listener


 - Client class (inheretes base client class)
     - Spawned once per conencted client (called from listener class)


Problems: 
 - ID's, need to store based on some metric. hostname could work, but UUID may be better?
     if the client generates it...
        collissions

     if the server generates it...
        client would need to know how to update its own ID

    this is neeeded for data storage in redis
    