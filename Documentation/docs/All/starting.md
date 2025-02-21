# **Starting WhisperNet**  

Before starting, ensure your **virtual environment is set up and activated**. Refer to the **Setup Section** for instructions.  

---

## **1. Starting the Server**  

Run the server to handle agent communications and command processing.  

```bash
cd Server
python3 app/whispernet.py
```

NOTE: Do not try to run `whispernet.py` if you are currently CD'd into the `app/` directory. There are some path related items that rely on the launch path being `Server/`

---

## **2. Starting the Web Interface**  

Launch the web interface for interacting with the server. Replace `<ADDRESS_OF_SERVER>` and `<PORT_OF_SERVER>` with the actual values.  

```bash
cd Web
python3 main --api-host http://<ADDRESS_OF_SERVER>:<PORT_OF_SERVER>/
```

NOTE: The computer you log into the web interface on needs to be able to reach the Server. API calls are done client side on the webserver, *to* the server.

---

## **3. Starting the Documentation Server**  

Serve the documentation locally for reference.  

```bash
cd Documentation
mkdocs serve
```

---

Once all components are running, the server, web interface, and documentation will be accessible.

## Useful Links

| Service         | URL                         | Notes                        |
|----------------|------------------------------|------------------------------|
| API Docs       | http://SERVER_IP:8081/       | Endpoint documentation/Swagger UI      |
| Web Interface  | http://WEBSERVER_IP:8080     | Main UI for interacting with the server |
| Documentation  | http://DOCS_IP:8000          | Project reference and setup guides |
