#include <stdio.h>
#include <windows.h>
#include <sddl.h> // For ConvertSidToStringSid if needed
#include <lmcons.h>

// CONVERT TO WHISPER_WINAPI!!

char *get_user_from_current_token(void)
{
    HANDLE hToken = NULL;
    char *result = NULL;

    // Open the access token associated with the current process.
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hToken))
    {
        fprintf(stderr, "OpenProcessToken failed. Error: %lu\n", GetLastError());
        return NULL;
    }

    // Determine the buffer size needed for the token information.
    DWORD dwSize = 0;
    GetTokenInformation(hToken, TokenUser, NULL, 0, &dwSize);

    PTOKEN_USER pTokenUser = (PTOKEN_USER)malloc(dwSize);
    if (pTokenUser == NULL)
    {
        fprintf(stderr, "Memory allocation error.\n");
        CloseHandle(hToken);
        return NULL;
    }

    // Retrieve the token information in a TOKEN_USER structure.
    if (!GetTokenInformation(hToken, TokenUser, pTokenUser, dwSize, &dwSize))
    {
        fprintf(stderr, "GetTokenInformation failed. Error: %lu\n", GetLastError());
        free(pTokenUser);
        CloseHandle(hToken);
        return NULL;
    }

    // Prepare buffers for name and domain.
    char name[256] = {0}, domain[256] = {0};
    DWORD nameSize = sizeof(name);
    DWORD domainSize = sizeof(domain);
    SID_NAME_USE sidType;

    if (!LookupAccountSid(NULL, pTokenUser->User.Sid, name, &nameSize, domain, &domainSize, &sidType))
    {
        fprintf(stderr, "LookupAccountSid failed. Error: %lu\n", GetLastError());
        free(pTokenUser);
        CloseHandle(hToken);
        return NULL;
    }

    // Allocate result string (format: "DOMAIN\username").
    size_t len = strlen(domain) + 1 + strlen(name) + 1;
    result = (char *)malloc(len);
    if (result)
    {
        snprintf(result, len, "%s\\%s", domain, name);
    }
    else
    {
        fprintf(stderr, "Memory allocation failed for result string.\n");
    }

    // Cleanup.
    free(pTokenUser);
    CloseHandle(hToken);
    return result;
}

char *username_to_sid(const char *username)
{
    char *sidStrCopy = NULL;
    PSID pSid = NULL;
    DWORD sidSize = 0;
    DWORD domainSize = 0;
    SID_NAME_USE sidType;

    // First call to determine buffer sizes.
    LookupAccountName(NULL, username, NULL, &sidSize, NULL, &domainSize, &sidType);

    pSid = malloc(sidSize);
    if (!pSid)
    {
        fprintf(stderr, "Memory allocation failed for SID buffer.\n");
        return NULL;
    }
    char *domainName = malloc(domainSize);
    if (!domainName)
    {
        fprintf(stderr, "Memory allocation failed for domain name buffer.\n");
        free(pSid);
        return NULL;
    }

    // Actual call to get the SID.
    if (!LookupAccountName(NULL, username, pSid, &sidSize, domainName, &domainSize, &sidType))
    {
        fprintf(stderr, "LookupAccountName failed. Error: %lu\n", GetLastError());
        free(pSid);
        free(domainName);
        return NULL;
    }
    free(domainName);

    // Convert the SID to a string.
    LPSTR sidStr = NULL;
    if (!ConvertSidToStringSidA(pSid, &sidStr))
    {
        fprintf(stderr, "ConvertSidToStringSid failed. Error: %lu\n", GetLastError());
        free(pSid);
        return NULL;
    }

    // Duplicate the returned string into our own heap memory.
    sidStrCopy = _strdup(sidStr);

    // Free resources allocated by Windows and our buffers.
    LocalFree(sidStr);
    free(pSid);
    return sidStrCopy;
}

char *get_current_token_sid(void)
{
    HANDLE hToken = NULL;
    char *result = NULL;

    // Open the access token for the current process.
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hToken))
    {
        fprintf(stderr, "OpenProcessToken failed. Error: %lu\n", GetLastError());
        return NULL;
    }

    // Determine the buffer size needed for token information.
    DWORD dwSize = 0;
    GetTokenInformation(hToken, TokenUser, NULL, 0, &dwSize);

    PTOKEN_USER pTokenUser = (PTOKEN_USER)malloc(dwSize);
    if (pTokenUser == NULL)
    {
        fprintf(stderr, "Memory allocation error.\n");
        CloseHandle(hToken);
        return NULL;
    }

    // Retrieve the token information.
    if (!GetTokenInformation(hToken, TokenUser, pTokenUser, dwSize, &dwSize))
    {
        fprintf(stderr, "GetTokenInformation failed. Error: %lu\n", GetLastError());
        free(pTokenUser);
        CloseHandle(hToken);
        return NULL;
    }

    // Convert the SID to a string.
    LPSTR sidStr = NULL;
    if (!ConvertSidToStringSidA(pTokenUser->User.Sid, &sidStr))
    {
        fprintf(stderr, "ConvertSidToStringSid failed. Error: %lu\n", GetLastError());
        free(pTokenUser);
        CloseHandle(hToken);
        return NULL;
    }

    // Duplicate the string into our own allocated memory.
    result = _strdup(sidStr);

    // Clean up resources.
    LocalFree(sidStr);
    free(pTokenUser);
    CloseHandle(hToken);

    return result;
}

char *get_user_from_sid_str(const char *sidString)
{
    if (sidString == NULL)
        return NULL;

    PSID pSid = NULL;
    // Convert the SID string to a binary SID.
    if (!ConvertStringSidToSidA(sidString, &pSid))
    {
        fprintf(stderr, "ConvertStringSidToSidA failed. Error: %lu\n", GetLastError());
        return NULL;
    }

    // Retrieve the username from the binary SID.
    char *userStr = get_user_from_binary_sid(pSid);

    // Free the binary SID allocated by ConvertStringSidToSidA.
    LocalFree(pSid);

    return userStr;
}

// Helper function to get user from a binary SID (PSID).
char *get_user_from_binary_sid(PSID pSid)
{
    if (pSid == NULL)
        return NULL;

    char name[256] = {0};
    char domain[256] = {0};
    DWORD nameSize = sizeof(name);
    DWORD domainSize = sizeof(domain);
    SID_NAME_USE sidType;

    if (!LookupAccountSidA(NULL, pSid, name, &nameSize, domain, &domainSize, &sidType))
    {
        fprintf(stderr, "LookupAccountSid failed. Error: %lu\n", GetLastError());
        return NULL;
    }

    // Allocate memory for the "DOMAIN\\username" string.
    size_t len = strlen(domain) + 1 + strlen(name) + 1;
    char *result = (char *)malloc(len);
    if (!result)
    {
        fprintf(stderr, "Memory allocation error.\n");
        return NULL;
    }
    snprintf(result, len, "%s\\%s", domain, name);
    return result;
}