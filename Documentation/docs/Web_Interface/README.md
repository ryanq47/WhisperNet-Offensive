# Whispernet Server Web Interface

This is the main interface for interacting with the Whispernet Server. All actions can be performed here, making it your primary point of interaction.

## Quickstart

1. Navigate to the `WebInterface` directory:

    ```bash
    cd WebInterface
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Start the web server:

    ```bash
    python3 main.py
    ```

    - Optional arguments:

        ```bash
        python3 main.py --help
        usage: main.py [-h] [--host HOST] [--port PORT]

        Run the NiceGUI app with optional host and port settings.

        Options:
        -h, --help   Show this help message and exit
        --host HOST  Set the host IP address (default: 127.0.0.1)
        --port PORT  Set the port number (default: 8080)
        ```

4. Access the Web Interface via the IP address or wait for the page to open automatically.
