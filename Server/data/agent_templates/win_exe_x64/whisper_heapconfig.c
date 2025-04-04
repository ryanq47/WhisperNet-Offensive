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

#include "StructOfStuff.h"
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

/* put in structs or soemthign .c*/
// Initialize structures and assign values to their members
int initStructs(HeapStore* heapStore) {

    // Initialize pointers to NULL to ensure safe cleanup later + clear data
    heapStore->tokenStore = NULL;
    heapStore->configStore = NULL;
    heapStore->securityStore = NULL;

    // Allocate memory for the security store structure
    SecurityStoreStruct* secstruct = malloc(sizeof(SecurityStoreStruct));
    if (secstruct == NULL) {
        fprintf(stderr, "Memory allocation failed for SecurityStoreStruct\n");
        return -1;
    }
    secstruct->xor_key = 0x01; // Hardcoded value (can be a macro)

    // Additional subsystems can be allocated and initialized here
    CurrentUserStoreStruct* curruserstruct = malloc(sizeof(CurrentUserStoreStruct));
    if (curruserstruct == NULL) {
        fprintf(stderr, "Memory allocation failed for CurrentUserStoreStruct\n");
        return -1;
    }

    // Assign the filled structure to the HeapStore
    heapStore->securityStore = secstruct;
    heapStore->currentUserStore = curruserstruct;

    return 0;
}

// Deinitialize structures and free allocated memory
void deinitStructs(HeapStore* heapStore) {
    if (heapStore == NULL) return;

    // Free securityStore if allocated
    if (heapStore->securityStore != NULL) {
        free(heapStore->securityStore);
        heapStore->securityStore = NULL;
    }

    // Free tokenStore if allocated (for future use)
    if (heapStore->currentUserStore != NULL) {
        free(heapStore->currentUserStore);
        heapStore->currentUserStore = NULL;
    }

    // Free tokenStore if allocated (for future use)
    if (heapStore->tokenStore != NULL) {
        free(heapStore->tokenStore);
        heapStore->tokenStore = NULL;
    }

    // Free configStore if allocated (for future use)
    if (heapStore->configStore != NULL) {
        free(heapStore->configStore);
        heapStore->configStore = NULL;
    }
}
/* [end] put in structs or soemthign .c*/
