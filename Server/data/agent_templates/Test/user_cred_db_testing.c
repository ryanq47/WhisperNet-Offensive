#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *username;
    char *ntlm_hash;
} UserCredential;

typedef struct {
    UserCredential **users;  // Pointer to an array of UserCredential pointers
    int user_count;
    int capacity;
} UserDatabase;

// Initialize database
UserDatabase *init_db(int capacity) {
    UserDatabase *db = malloc(sizeof(UserDatabase));
    db->users = malloc(capacity * sizeof(UserCredential *));  // Allocate space for pointers
    db->user_count = 0;
    db->capacity = capacity;
    return db;
}

// Add a user
void add_user(UserDatabase *db, const char *username, const char *ntlm_hash) {
    if (db->user_count >= db->capacity) {
        db->capacity *= 2;
        db->users = realloc(db->users, db->capacity * sizeof(UserCredential *));  // Expand the array
    }

    db->users[db->user_count] = malloc(sizeof(UserCredential));  // Allocate struct
    db->users[db->user_count]->username = strdup(username);  // Allocate & copy string
    db->users[db->user_count]->ntlm_hash = strdup(ntlm_hash);
    
    db->user_count++;
}

// Display users
void display_users(const UserDatabase *db) {
    for (int i = 0; i < db->user_count; i++) {
        printf("Username: %s, NTLM Hash: %s\n", db->users[i]->username, db->users[i]->ntlm_hash);
    }
}

// Free database
void free_db(UserDatabase *db) {
    for (int i = 0; i < db->user_count; i++) {
        free(db->users[i]->username);
        free(db->users[i]->ntlm_hash);
        free(db->users[i]);
    }
    free(db->users);
    free(db);
}

int main() {
    UserDatabase *db = init_db(2);

    add_user(db, "admin", "31d6cfe0d16ae931b73c59d7e0c089c0");
    add_user(db, "user1", "c8e1b8b3e0f5f3f2e7f5b7e9b7a6f0b4");

    display_users(db);
    free_db(db);

    return 0;
}
