
// makes SURE this is only called once/doesn't re-init things. May need to get split into .c and .h if ever called from
// more than once place
#pragma once

#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//typedef struct
//{
//    char agent_id[37]; // UUID as a string (max 36 chars + null terminator)
//    char* command_result_data; // Variable-length string
//    char* command_id; // Variable-length string
//} OutboundJsonDataStruct;
//
//typedef struct
//{
//    char* command_id;
//    char* command; // Variable-length string
//    char* args; // Variable-length string
//
//} InboundJsonDataStruct;

typedef struct
{
    char* command_result_data; // Variable-length string
    char* command_id; // Variable-length string
    char* agent_id;
} OutboundJsonDataStruct;

typedef struct
{
    char* command_id;
    char* command; // Variable-length string
    char* args; // Variable-length string
    char* agent_id;
} InboundJsonDataStruct;

// Function declarations (fixes conflicting types issue)
char* encode_json(const char* uuid, const char* command_result_data, const char* command_id);
InboundJsonDataStruct decode_command_json(const char* json_str);
// void free_json_data(OutboundJsonDataStruct *OutboundJsonDataStruct);

// how to use
// int main() {
//     // Example UUID as a string
//     const char *uuid = "550e8400-e29b-41d4-a716-446655440000";
//
//     // Example command_result_data string
//     const char *command_result_data = "Example variable-length string command_result_data.";
//
//     // Encode JSON
//     char *json_str = encode_json(uuid, command_result_data);
//     if (!json_str) {
//         fprintf(stderr, "Failed to encode JSON\n");
//         return 1;
//     }
//
//     printf("Encoded JSON: %s\n", json_str);
//
//     // Decode JSON
//     OutboundJsonDataStruct decoded = decode_json(json_str);
//     printf("Decoded UUID: %s\n", decoded.agent_id);
//     printf("Decoded command_result_data: %s\n", decoded.command_result_data);
//
//     // Cleanup
//     SecureFree(json_str);
//     SecureFree(decoded.command_result_data);
//
//     return 0;
// }

/**
 * Encodes a OutboundJsonDataStruct structure into a JSON string.
 */
char* encode_json(const char* agent_id, const char* command_result_data, const char* command_id)
{
    cJSON* root = cJSON_CreateObject();
    if (!root)
        return NULL;

    cJSON_AddStringToObject(root, "agent_id", agent_id);
    cJSON_AddStringToObject(root, "command_result_data", command_result_data);
    cJSON_AddStringToObject(root, "command_id", command_id);

    char* json_str = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);

    return json_str; // Caller must free this
}

/**
 * Decodes a JSON string into a OutboundJsonDataStruct structure.
 */
InboundJsonDataStruct decode_command_json(const char* json_str)
{
    InboundJsonDataStruct result = { NULL };

    cJSON* root = cJSON_Parse(json_str);
    if (!root)
        return result;

    // cJSON *agent_id = cJSON_GetObjectItemCaseSensitive(root, "agent_id");
    cJSON* command_id = cJSON_GetObjectItemCaseSensitive(root, "command_id");
    cJSON* command = cJSON_GetObjectItemCaseSensitive(root, "command");
    cJSON* args = cJSON_GetObjectItemCaseSensitive(root, "args");

    if (cJSON_IsString(command_id) && command_id->valuestring) {
        result.command_id = strdup(command_id->valuestring); // Caller must free
    }

    if (cJSON_IsString(command) && command->valuestring) {
        result.command = strdup(command->valuestring); // Caller must free
    }
    if (cJSON_IsString(args) && args->valuestring) {
        result.args = strdup(args->valuestring); // Caller must free
    }

    cJSON_Delete(root);
    return result;
}
