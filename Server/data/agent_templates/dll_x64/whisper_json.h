
// makes SURE this is only called once/doesn't re-init things. May need to get split into .c and .h if ever called from
// more than once place
#pragma once

#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct
{
    char id[37]; // UUID as a string (max 36 chars + null terminator)
    char* data; // Variable-length string
    char* command_id; // Variable-length string
} JsonData;

typedef struct
{
    char* command_id;
    char* command; // Variable-length string
    char* args; // Variable-length string

} JsonDataCommand;

// Function declarations (fixes conflicting types issue)
char* encode_json(const char* uuid, const char* data, const char* command_id);
JsonDataCommand decode_command_json(const char* json_str);
// void free_json_data(JsonData *jsonData);

// how to use
// int main() {
//     // Example UUID as a string
//     const char *uuid = "550e8400-e29b-41d4-a716-446655440000";
//
//     // Example data string
//     const char *data = "Example variable-length string data.";
//
//     // Encode JSON
//     char *json_str = encode_json(uuid, data);
//     if (!json_str) {
//         fprintf(stderr, "Failed to encode JSON\n");
//         return 1;
//     }
//
//     printf("Encoded JSON: %s\n", json_str);
//
//     // Decode JSON
//     JsonData decoded = decode_json(json_str);
//     printf("Decoded UUID: %s\n", decoded.id);
//     printf("Decoded Data: %s\n", decoded.data);
//
//     // Cleanup
//     SecureFree(json_str);
//     SecureFree(decoded.data);
//
//     return 0;
// }

/**
 * Encodes a JsonData structure into a JSON string.
 */
char* encode_json(const char* uuid, const char* data, const char* command_id)
{
    cJSON* root = cJSON_CreateObject();
    if (!root)
        return NULL;

    cJSON_AddStringToObject(root, "id", uuid);
    cJSON_AddStringToObject(root, "data", data);
    cJSON_AddStringToObject(root, "command_id", command_id);

    char* json_str = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);

    return json_str; // Caller must free this
}

/**
 * Decodes a JSON string into a JsonData structure.
 */
JsonDataCommand decode_command_json(const char* json_str)
{
    JsonDataCommand result = { NULL };

    cJSON* root = cJSON_Parse(json_str);
    if (!root)
        return result;

    // cJSON *id = cJSON_GetObjectItemCaseSensitive(root, "id");
    cJSON* command_id = cJSON_GetObjectItemCaseSensitive(root, "command_id");
    cJSON* command = cJSON_GetObjectItemCaseSensitive(root, "command");
    cJSON* args = cJSON_GetObjectItemCaseSensitive(root, "args");

    if (cJSON_IsString(command_id) && command_id->valuestring) {
        result.command_id = _strdup(command_id->valuestring); // Caller must free
    }

    if (cJSON_IsString(command) && command->valuestring) {
        result.command = _strdup(command->valuestring); // Caller must free
    }
    if (cJSON_IsString(args) && args->valuestring) {
        result.args = _strdup(args->valuestring); // Caller must free
    }

    cJSON_Delete(root);
    return result;
}
