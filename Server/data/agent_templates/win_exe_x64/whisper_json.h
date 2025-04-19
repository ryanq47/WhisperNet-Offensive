
// makes SURE this is only called once/doesn't re-init things. May need to get split into .c and .h if ever called from
// more than once place
#pragma once

#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// typedef struct
//{
//     char agent_id[37]; // UUID as a string (max 36 chars + null terminator)
//     char* command_result_data; // Variable-length string
//     char* command_id; // Variable-length string
// } OutboundJsonDataStruct;
//
// typedef struct
//{
//     char* command_id;
//     char* command; // Variable-length string
//     char* args; // Variable-length string
//
// } InboundJsonDataStruct;

typedef struct
{
    char *command_result_data; // Variable-length string
    char *command_id;          // Variable-length string
    char *agent_id;
    // metadata fields
    char *int_ip;
    char *ext_ip;
    char *user;
    char *os;
} OutboundJsonDataStruct;

typedef struct
{
    char *command_id;
    char *command; // Variable-length string
    char *args;    // Variable-length string
    char *agent_id;
} InboundJsonDataStruct;

// Function declarations (fixes conflicting types issue)
char *encode_json(const char *uuid, const char *command_result_data, const char *command_id, const char *int_ip, const char *ext_ip, const char *os, const char *user);
InboundJsonDataStruct decode_command_json(const char *json_str);
// void free_json_data(OutboundJsonDataStruct *OutboundJsonDataStruct);
