## Docker Docs:


1. Build docker container
 - Gets right toolchains installed, etc. 


2. RUN docker container, with appropriate args. 

Manual Run
    ```
        docker run --rm -v $(pwd)/agents/windows/loaders/local_shellcode_exectution:/usr/src/myapp -v $(pwd)/output:/output -e BINARY_NAME="custom_binary_name" -e WATCH_DIR="/usr/src/myapp" -e INTERVAL=3 -e PLATFORM="x64" dev-rust-app

    ```
Script now waits for a .toml to show up...
Then, copy in folder to compile. 

    ```
        docker cp agents/windows/loaders/local_shellcode_execution/.

        # the . is important as it gets the contens of the folder, not the folder itself 
    ```

    a. This builds the executable with the correct eveything

3. Executable is outputted to data/compiled folder.


Works - just need to port to the application now