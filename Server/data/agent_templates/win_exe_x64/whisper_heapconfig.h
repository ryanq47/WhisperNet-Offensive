#pragma once
#include <windows.h>

// StoreStructs first
typedef struct {
    /*
    * A struct for holding security related information.
    */
    int xor_key;
} SecurityStoreStruct;

typedef struct {
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
    char* username;
    char* password;
    char* domain;
    PSID userSid;
    HANDLE token;
    LUID logonId;
    DWORD sessionId;
    LPWSTR profilePath;
} CurrentUserStoreStruct;

// Big Struct last
typedef struct {
    /*
    * A struct for holding various subsystem pointers for the agent.
    * Expandable design for future development.
    */
    void* tokenStore;
    void* configStore;   // Config object
    SecurityStoreStruct* securityStore; // Use the struct types here for better type handling
    CurrentUserStoreStruct* currentUserStore; // Use the struct types here for better type handling

} HeapStore;