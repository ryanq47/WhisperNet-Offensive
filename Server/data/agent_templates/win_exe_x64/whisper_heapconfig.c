/*
*******************************************************************************************
* Module: whisper_heapconfig.c
*
* Description:
*   This module implements a modular, expandable data storage system for an agent application.
*   The primary container is the HeapStore struct, which aggregates pointers to various subsystem
*   structures that hold configuration and runtime state for the agent.
*
* Structures:
*   HeapStore:
*        ONE heap store should exist per execution. This is immediatlet set up in main
*
*     - tokenStore:         Pointer to the token subsystem (reserved for future use).
*     - configStore:        Pointer to the configuration subsystem (reserved for future use).
*     - securityStore:      Pointer to SecurityStoreStruct, which holds security-related data (e.g., xor_key).
*     - currentUserStore:   Pointer to CurrentUserStoreStruct, which holds current user information.
*     - agentStore:         Pointer to AgentStoreStruct, which contains agent-specific data (e.g., agent_id).
*     - agentBehaviorStore: Pointer to AgentBehaviorStruct, which holds runtime behavior settings such as
*                           execution mode and sleep time, and includes a synchronization lock.
*
*   SecurityStoreStruct:
*     - xor_key: A hardcoded XOR key used for simple security operations or obfuscation.
*
*   CurrentUserStoreStruct:
*     - username:               Pointer to a string containing the current user's name.
*     - password:               Pointer to a string containing the current user's password.
*     - domain:                 Pointer to a string containing the current user's domain.
*     - userSid:                Pointer to the current user's security identifier (SID).
*     - token:                  Handle to the current user's access token.
*     - logonId:                Locally unique identifier (LUID) for the user's logon session.
*     - sessionId:              Identifier for the user's session (DWORD).
*     - profilePath:            Pointer to a wide-character string (LPWSTR) containing the path to
*                               the user's profile.
*
*
*   AgentStoreStruct:
*     - agent_id: A character array (typically storing a unique identifier such as a UUID) for the agent.
*
*   AgentBehaviorStruct:
*     - sleep_time:         The delay (in seconds) between agent execution cycles.
*     - execution_mode:     Indicates the agent's operating mode (e.g., synchronous or asynchronous).
*     - agent_config_lock:  An SRWLock used to protect access to configuration and runtime settings.
*
* Connections:
*   The HeapStore struct is the central repository that aggregates all subsystem structures.
*   Each subsystem is dynamically allocated and linked within HeapStore via its pointers.
*   The getters and setters operate on the agentBehaviorStore to ensure thread-safe modification and
*   retrieval of runtime configuration values.
*
* Function Information:
*
*   int initStructs(HeapStore *heapStore)
*     - Initializes all subsystem pointers in the HeapStore structure.
*     - Dynamically allocates memory for SecurityStoreStruct, CurrentUserStoreStruct, AgentStoreStruct, and
*       AgentBehaviorStruct.
*     - Sets initial values, such as the XOR key for the security store and default values for the
*       agent behavior (sleep time, execution mode, etc.).
*     - Returns 0 on success or -1 if any memory allocation fails.
*
*   void deinitStructs(HeapStore *heapStore)
*     - Deallocates all memory allocated for subsystem structures within HeapStore.
*     - Resets pointers to NULL to prevent dangling references.
*
*   void set_execution_mode(ExecutionMode mode, HeapStore *heapStorePointer)
*     - Sets the agent's execution mode (e.g., synchronous/asynchronous) in a thread-safe manner.
*     - Uses an SRWLock to ensure exclusive access during modification.
*
*   ExecutionMode get_execution_mode(HeapStore *heapStorePointer)
*     - Retrieves the current agent execution mode in a thread-safe manner.
*     - Uses an SRWLock to ensure safe access to the configuration.
*
*   void set_sleep_time(DWORD new_time, HeapStore *heapStorePointer)
*     - Updates the sleep time value in the agent behavior configuration in a thread-safe manner.
*
*   DWORD get_sleep_time(HeapStore *heapStorePointer)
*     - Retrieves the current sleep time value from the agent behavior configuration in a thread-safe manner.
*
* Goal:
*   To provide a clear, modular, and expandable system for managing an agent's various subsystems,
*   enabling easy development and maintenance while ensuring proper synchronization and memory management.
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
// Current User funcs
// -----------------------------------------
HANDLE get_current_stored_token(HeapStore *heapStorePointer)
{
    // Acquire the lock before accessing the token
    AcquireSRWLockExclusive(&heapStorePointer->currentUserStore->token);
    DEBUG_LOG("GET TOKEN");

    HANDLE token = heapStorePointer->currentUserStore->token;

    if (!token)
    {
        // Release the lock before retrieving the process token.
        ReleaseSRWLockExclusive(&heapStorePointer->currentUserStore->token);

        // If no token is stored, retrieve and return the current process token.
        // is just a fallback incase a toekn doesn't exist or something
        token = GetCurrentProcessToken();
        if (!token)
        {
            DEBUG_LOG("Failed to retrieve current process token.\n");
        }
        return token;
    }

    // Release the lock before returning the stored token.
    ReleaseSRWLockExclusive(&heapStorePointer->currentUserStore->token);
    return token;
}

void set_current_stored_token(HeapStore *heapStorePointer, HANDLE hToken)
{
    AcquireSRWLockExclusive(&heapStorePointer->currentUserStore->token);

    heapStorePointer->currentUserStore->token = hToken;

    ReleaseSRWLockExclusive(&heapStorePointer->currentUserStore->token);
}

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