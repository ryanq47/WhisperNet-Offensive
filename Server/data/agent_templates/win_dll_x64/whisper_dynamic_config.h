#ifndef DYNAMIC_CONFIG_H
#define DYNAMIC_CONFIG_H

#include <windows.h>

// Struct to store global configuration
typedef struct {
    DWORD sleep_time;  // Sleep duration in milliseconds
    DWORD jitter;      // Jitter percentage
} AgentConfig;

typedef enum {
    EXEC_MODE_ASYNC,
    EXEC_MODE_SYNC,
    // Add other modes as needed
} ExecutionMode;

// Declare a global pointer to the config struct
extern AgentConfig g_agent_config;
extern ExecutionMode g_execution_mode;

// Function prototypes
void init_config(DWORD sleep_time, DWORD jitter);
void set_sleep_time(DWORD new_time);
DWORD get_sleep_time();
void set_execution_mode(ExecutionMode mode);
ExecutionMode get_execution_mode();
void initialize_critical_sections();

#endif // CONFIG_H
