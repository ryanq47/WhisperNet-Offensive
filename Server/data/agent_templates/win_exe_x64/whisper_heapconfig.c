/*
*******************************************************************************************
* File: StructOfStuff.cpp
*
* Description:
*   This application demonstrates the creation, initialization, and cleanup of a modular data
*   structure in C, designed for expandability. The primary structure, HeapStore, contains pointers
*   to various subsystem structures (e.g., SecurityStoreStruct) that can be extended as needed.
*   This design allows easier development and maintenance by centralizing related data and providing
*   robust initialization and deinitialization routines.
*
* Goal:
*   To provide a clean, modular design for managing different components in an application, ensuring
*   proper memory management and making it straightforward to add or remove subsystems.
*******************************************************************************************
*/

#include "whisper_structs.h"
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include "whisper_config.h"

/* put in structs or soemthign .c*/
// Initialize structures and assign values to their members
int initStructs(HeapStore *heapStore)
{

    // Initialize pointers to NULL to ensure safe cleanup later + clear data
    heapStore->tokenStore = NULL;
    heapStore->configStore = NULL;
    heapStore->securityStore = NULL;
    heapStore->currentUserStore = NULL;

    // -----------------------------------------
    // SecurityStoreStruct
    // -----------------------------------------
    SecurityStoreStruct *secstruct = malloc(sizeof(SecurityStoreStruct));
    if (secstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for SecurityStoreStruct\n");
        return -1;
    }
    secstruct->xor_key = 0x01; // Hardcoded value (can be a macro)

    // -----------------------------------------
    // CurrentUserStoreStruct
    // -----------------------------------------
    CurrentUserStoreStruct *curruserstruct = malloc(sizeof(CurrentUserStoreStruct));
    if (curruserstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for CurrentUserStoreStruct\n");
        return -1;
    }

    // -----------------------------------------
    // AgentStoreStruct
    // -----------------------------------------
    AgentStoreStruct *agentstruct = malloc(sizeof(AgentStoreStruct));
    if (agentstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for AgentStoreStruct\n");
        return -1;
    }

    // -----------------------------------------
    // AgentBehaviorStruct
    // -----------------------------------------
    AgentBehaviorStruct *agentbehaviorstruct = malloc(sizeof(AgentBehaviorStruct));
    if (agentbehaviorstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for AgentBehaviorStruct\n");
        return -1;
    }
    agentbehaviorstruct->sleep_time = 60;
    agentbehaviorstruct->execution_mode = EXEC_MODE_ASYNC;
    InitializeSRWLock(&agentbehaviorstruct->agent_config_lock);

    // Assign the filled structure to the HeapStore
    heapStore->securityStore = secstruct;
    heapStore->currentUserStore = curruserstruct;
    heapStore->agentStore = agentstruct;
    heapStore->agentBehaviorStore = agentbehaviorstruct;

    return 0;
}

// Deinitialize structures and free allocated memory
void deinitStructs(HeapStore *heapStore)
{
    if (heapStore == NULL)
        return;

    // Free securityStore if allocated
    if (heapStore->securityStore != NULL)
    {
        free(heapStore->securityStore);
        heapStore->securityStore = NULL;
    }

    if (heapStore->agentBehaviorStore != NULL)
    {
        free(heapStore->agentBehaviorStore);
        heapStore->agentBehaviorStore = NULL;
    }

    // Free securityStore if allocated
    if (heapStore->agentStore != NULL)
    {
        free(heapStore->agentStore);
        heapStore->agentStore = NULL;
    }

    // Free tokenStore if allocated (for future use)
    if (heapStore->currentUserStore != NULL)
    {
        free(heapStore->currentUserStore);
        heapStore->currentUserStore = NULL;
    }

    // Free tokenStore if allocated (for future use)
    if (heapStore->tokenStore != NULL)
    {
        free(heapStore->tokenStore);
        heapStore->tokenStore = NULL;
    }

    // Free configStore if allocated (for future use)
    if (heapStore->configStore != NULL)
    {
        free(heapStore->configStore);
        heapStore->configStore = NULL;
    }
}
/* [end] put in structs or soemthign .c*/

// -----------------------------------------
// AgentBehaviorFuncs
// -----------------------------------------

// Execution Mode functions (protected by g_execution_mode_mutex)

void set_execution_mode(ExecutionMode mode, HeapStore *heapStorePointer)
{
    DEBUG_LOG("B4 ECS");

    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DEBUG_LOG("SET CONFIG");

    heapStorePointer->agentBehaviorStore->execution_mode = mode;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DEBUG_LOG("LEAVE ECS");
}

ExecutionMode get_execution_mode(HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    ExecutionMode mode = heapStorePointer->agentBehaviorStore->execution_mode; // Copy the value
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return mode;
}

void set_sleep_time(DWORD new_time, HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    heapStorePointer->agentBehaviorStore->sleep_time = new_time;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}

DWORD get_sleep_time(HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DWORD sleep_time = heapStorePointer->agentBehaviorStore->sleep_time;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return sleep_time;
}