#include "whisper_json.h"

char *encode_json(const char *agent_id, const char *command_result_data, const char *command_id, const char *int_ip, const char *ext_ip, const char *os, const char *user)
/**
 * encode_json - Creates a JSON-encoded string representing the result of a command execution.
 *
 * This function constructs a JSON object with the given agent ID, command result data, and
 * command ID. It also includes a "metadata" sub-object containing additional static fields:
 * "ext_ip", "int_ip", and "context".
 *
 * Example output:
 * {
 *   "agent_id": "abc123",
 *   "command_result_data": "some data",
 *   "command_id": "cmd456",
 *   "metadata": {
 *     "os": "os",
 *     "ext_ip": "ext_ip",
 *     "int_ip": "int_ip",
 *     "context": "context"
 *   }
 * }
 *
 * @param agent_id             A string representing the unique ID of the agent.
 * @param command_result_data  A string containing the result of a command execution.
 * @param command_id           A string identifier for the command.
 *
 * @return A heap-allocated JSON string representation of the data.
 *         The caller is responsible for freeing the returned string.
 *         Returns NULL if memory allocation fails.
 */
{
    cJSON *root = cJSON_CreateObject();
    if (!root)
        return NULL;

    // Add top-level fields
    cJSON_AddStringToObject(root, "agent_id", agent_id);
    cJSON_AddStringToObject(root, "command_result_data", command_result_data);
    cJSON_AddStringToObject(root, "command_id", command_id);

    // Create metadata object
    cJSON *metadata = cJSON_CreateObject();
    if (!metadata)
    {
        cJSON_Delete(root);
        return NULL;
    }

    // Add metadata fields
    cJSON_AddStringToObject(metadata, "os", os);
    cJSON_AddStringToObject(metadata, "ext_ip", ext_ip);
    cJSON_AddStringToObject(metadata, "int_ip", int_ip);
    cJSON_AddStringToObject(metadata, "user", user);

    // Add metadata to root
    cJSON_AddItemToObject(root, "metadata", metadata);

    // Convert to string
    char *json_str = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);

    return json_str; // Caller must free this
}

InboundJsonDataStruct decode_command_json(const char *json_str)
/**
 * decode_command_json - Parses a JSON string containing command information into a structured format.
 *
 * This function takes a JSON string representing an inbound command and extracts the fields:
 * "command_id", "command", and "args". These are stored in an InboundJsonDataStruct for further use.
 *
 * Expected input format:
 * {
 *   "command_id": "111-111-111-111",
 *   "command": "shell",
 *   "args": "whoami"
 * }
 *
 * The returned struct contains dynamically allocated strings for each field if present and valid.
 *
 * @param json_str  A null-terminated JSON string to parse.
 *
 * @return An InboundJsonDataStruct containing the parsed data. If parsing fails, all fields are NULL.
 *         The caller is responsible for freeing the returned strings in the struct (via `free()`).
 */
{
    InboundJsonDataStruct result = {NULL};

    cJSON *root = cJSON_Parse(json_str);
    if (!root)
        return result;

    // cJSON *agent_id = cJSON_GetObjectItemCaseSensitive(root, "agent_id");
    cJSON *command_id = cJSON_GetObjectItemCaseSensitive(root, "command_id");
    cJSON *command = cJSON_GetObjectItemCaseSensitive(root, "command");
    cJSON *args = cJSON_GetObjectItemCaseSensitive(root, "args");

    if (cJSON_IsString(command_id) && command_id->valuestring)
    {
        result.command_id = _strdup(command_id->valuestring); // Caller must free
    }

    if (cJSON_IsString(command) && command->valuestring)
    {
        result.command = _strdup(command->valuestring); // Caller must free
    }
    if (cJSON_IsString(args) && args->valuestring)
    {
        result.args = _strdup(args->valuestring); // Caller must free
    }

    cJSON_Delete(root);
    return result;
}
