#pragma once

#include <windows.h>

// Define the CredentialStore struct
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

typedef struct {
    UserCredential *head;
    int count;
} CredentialStore;

// Function prototypes
CredentialStore *get_credential_store();  // Singleton getter
void add_credential(const char *username, const char *domain,
                    const char *ntlm_hash, const char *lm_hash, const char *plaintext_pass,
                    const char *kerb_ticket, const char *aes128_key, const char *aes256_key,
                    const char *dpapi_masterkey);
void display_credentials();
void free_store();
