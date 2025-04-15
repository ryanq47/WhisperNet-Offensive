#pragma once
#include <windows.h>
// structs for each substruct needed

// -----------------------------------------
// AgentBehaviorStructs
// -----------------------------------------
typedef enum
{
    EXEC_MODE_ASYNC,
    EXEC_MODE_SYNC,
} ExecutionMode;

// -----------------------------------------
// Substructs
// -----------------------------------------

// StoreStructs first
typedef struct
{
    /*
     * A struct for holding security related information.
     */
    int xor_key;
} SecurityStoreStruct;

typedef struct
{
    /*
     * A struct for holding the CURRENT user information.
     * This will be used for all current operations involving users. Ex,
     * load a differnet token in here and that will be the currently used token
     *
     * username:    Pointer to a string containing the user's name.
     * password:    Pointer to a string containing the user's password.
     * domain:      Pointer to a string containing the user's domain.
     * userSid:     Pointer to the user's security identifier (SID).
     * token:       Handle to the user's access token.
     * logonId:     Locally unique identifier (LUID) for the logon session.
     * sessionId:   Identifier for the user's session.
     * profilePath: Pointer to a wide string containing the path to the user's profile.
     */
    char *username;
    char *password;
    char *domain;
    PSID userSid;
    HANDLE token;
    LUID logonId;
    DWORD sessionId;
    LPWSTR profilePath;
} CurrentUserStoreStruct;

typedef struct
{
    /*
    * A struct for holding the AGENT information.

    */

    char agent_id[37];
    // os version
    char *os;

} AgentStoreStruct;

typedef struct
{
    /*
    * A struct for holding the AGENT information.

    */

    char *ext_ip;
    char *int_ip;

} AgentNetworkStruct;

typedef struct
{
    /*
    * A struct for holding the AGENT behavior info/config

    */
    DWORD sleep_time;
    ExecutionMode execution_mode;
    // more values...
    SRWLOCK agent_config_lock;

} AgentBehaviorStruct;

// Big Struct last
typedef struct
{
    /*
     * A struct for holding various subsystem pointers for the agent.
     * Expandable design for future development.
     */
    void *tokenStore;
    void *configStore;                        // Config object
    SecurityStoreStruct *securityStore;       // Use the struct types here for better type handling
    CurrentUserStoreStruct *currentUserStore; // Use the struct types here for better type handling
    AgentStoreStruct *agentStore;
    AgentBehaviorStruct *agentBehaviorStore;
    AgentNetworkStruct *agentNetworkStore;

} HeapStore;

// -----------------------------------------
// Prototypes
// -----------------------------------------
// prototypes down here, so they can take advatage of the above
void set_sleep_time(DWORD new_time, HeapStore *heapStorePointer);
DWORD get_sleep_time(HeapStore *heapStorePointer);
void set_execution_mode(ExecutionMode mode, HeapStore *heapStorePointer);
ExecutionMode get_execution_mode(HeapStore *heapStorePointer);
void initialize_critical_sections();
void set_current_stored_token(HeapStore *heapStorePointer, HANDLE hToken);
char *get_current_username(HeapStore *heapStorePointer);
void set_current_username(HeapStore *heapStorePointer, char *username);
