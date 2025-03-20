#include "whisper_dynamic_config.h"
#include "whisper_config.h"
/*
...

Heap based storage config system
*/

/*
Initialize config object for the agent.

Uses heap based storage for values, instead of globals, in order to maintain
shellcode compatability.
*/
CONFIG *init_config()
{
    CONFIG *config = (CONFIG *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(CONFIG));
    if (!config)
    {
        DEBUG_LOG("CONFIG FAILED TO ALLOCATE");
        return NULL;
    }

    // can edit at runtime with: config->sleep_time = 2000; // changed from 5000 to 2000 ms
    config->sleep_time = 60;
    config->execution_mode = EXEC_MODE_ASYNC;

    // Initialize the SRWLOCK by assigning the constant initializer
    // config->agent_config_lock = SRWLOCK_INIT;
    InitializeSRWLock(&config->agent_config_lock);

    return config;
}

// Agent Config functions (protected by g_agent_config_mutex)
void set_sleep_time(DWORD new_time, CONFIG *config)
{
    AcquireSRWLockExclusive(&config->agent_config_lock);
    config->sleep_time = new_time;
    ReleaseSRWLockExclusive(&config->agent_config_lock);
}

DWORD get_sleep_time(CONFIG *config)
{
    AcquireSRWLockExclusive(&config->agent_config_lock);
    DWORD sleep_time = config->sleep_time;
    ReleaseSRWLockExclusive(&config->agent_config_lock);
    return sleep_time;
}

// Execution Mode functions (protected by g_execution_mode_mutex)
void set_execution_mode(ExecutionMode mode, CONFIG *config)
{
    DEBUG_LOG("B4 ECS");

    AcquireSRWLockExclusive(&config->agent_config_lock);
    DEBUG_LOG("SET CONFIG");

    config->execution_mode = mode;
    ReleaseSRWLockExclusive(&config->agent_config_lock);
    DEBUG_LOG("LEAVE ECS");
}

ExecutionMode get_execution_mode(CONFIG *config)
{
    AcquireSRWLockExclusive(&config->agent_config_lock);
    ExecutionMode mode = config->execution_mode; // Copy the value
    ReleaseSRWLockExclusive(&config->agent_config_lock);
    return mode;
}
