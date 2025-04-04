#ifndef DYNAMIC_CONFIG_H
#define DYNAMIC_CONFIG_H

#include <windows.h>
#include "whisper_structs.h"
// Struct to store global configuration
typedef struct
{
    DWORD sleep_time; // Sleep duration in milliseconds
    DWORD jitter;     // Jitter percentage
} AgentConfig;

// typedef enum
// {
//     EXEC_MODE_ASYNC,
//     EXEC_MODE_SYNC,
//     // Add other modes as needed
// } ExecutionMode;

// typedef struct
// {
//     DWORD sleep_time;
//     ExecutionMode execution_mode;
//     // more values...
//     SRWLOCK agent_config_lock;

// } CONFIG;

// Args for passing to each exec func cuz threads and we need it in one spot
// typedef struct
// {
//     char *agent_id;
//     CONFIG *config;
// } EXEC_ARGS;

// Function prototypes
// CONFIG *init_config();
// void set_sleep_time(DWORD new_time, HeapStore *heapStorePointer);
// DWORD get_sleep_time(CONFIG *config);
// void set_execution_mode(ExecutionMode mode, ;
// ExecutionMode get_execution_mode(HeapStore *heapStorePointer);
// void initialize_critical_sections();

#endif // CONFIG_H
