#ifndef CONFIG_H
#define CONFIG_H

#include <windows.h>

// Struct to store global configuration
typedef struct {
    DWORD sleep_time;  // Sleep duration in milliseconds
    DWORD jitter;      // Jitter percentage
} AgentConfig;

// Declare a global pointer to the config struct
extern AgentConfig g_agent_config;

// Function prototypes
void init_config(DWORD sleep_time, DWORD jitter);
void set_sleep_time(DWORD new_time);
DWORD get_sleep_time();

#endif // CONFIG_H
