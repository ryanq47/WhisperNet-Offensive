# Whispernet API (`whisper_api.h`)

WhisperNet's API serves as a wrapper around WinAPI (`windows.h`) functions, designed to enhance OPSEC by evading AV/EDR detection. Since these APIs are commonly flagged, the goal is to obscure their usage while maintaining full functionality.  

All function names and arguments remain identical to their Windows API counterparts, except with "whisper" prefixed to the function names.  

**Example:**  
`VirtualAllocEx(...)` → `WhisperVirtualAllocEx(...)`

---

# **Current Capabilities**  

The current list of capabilites that `whisper_api.h` can do

As I learn more, the list of capabilites, and functions in here will expand.

## **Dynamic Function Resolution**  

### **Why It Matters:**  
By removing imports from the IAT (Import Address Table), this technique helps evade AV/EDR detection. Security solutions often analyze the IAT to determine an executable’s behavior, making dynamic resolution a key OPSEC enhancement.

Note, this alone will *not* get you around EDR's, however I've seen some success with Windows Defender

### **How It Works**:

Here's a Whisper function directly out of `whisper_api.h`

```
//Fun Note, you technically don't need to declare this type, gcc will compile without it, but it can lead to weird errors.
typedef LPVOID (WINAPI *VirtualAllocEx_t)(
	HANDLE hProcess,
	LPVOID lpAddress,
	SIZE_T dwSize,
	DWORD  flAllocationType,
	DWORD  flProtect
);

LPVOID WhisperVirtualAllocEx(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect) {
    /*
    Wrapper for VirtualAllocEx()

    LPVOID WhisperVirtualAllocEx(
      [in]           HANDLE hProcess,
      [in, optional] LPVOID lpAddress,
      [in]           SIZE_T dwSize,
      [in]           DWORD  flAllocationType,
      [in]           DWORD  flProtect
    );
    */

    printf("WhisperVirtualAllocEx\n");

    // Get the actual function address using `ResolveFunction`, and cast to the type of `VirtualAllocEx_t`
    VirtualAllocEx_t pVirtualAllocEx = (VirtualAllocEx_t)ResolveFunction("kernel32.dll", "VirtualAllocEx");
    //on failure, return.
    if (!pVirtualAllocEx) {
        printf("[!] Failed to resolve VirtualAllocEx.\n");
        return NULL;
    }

    //If successful, call function
    // Pass the args through to this function
    LPVOID result = pVirtualAllocEx(hProcess, lpAddress, dwSize, flAllocationType, flProtect);
    if (!result) {
        printf("[!] VirtualAllocEx failed. Error: %d\n", GetLastError());
    }

    //and return the result, which is a memory address 
    return result;
}

```

### **Limitations & Considerations**:



# Template:

### **Why It Matters**:
[Explain why this capability is important, including its impact on OPSEC, AV/EDR evasion, or overall stealth.]

### **How It Works**:
[Briefly describe the technical implementation or methodology used to achieve this capability.]

### **Limitations & Considerations**:
[Highlight any known drawbacks, detection risks, or scenarios where this approach may not be effective. Provide notes on potential mitigations if applicable.]


# List of currently supported Functions:


### CreateProcessA
```
typedef BOOL (WINAPI *CreateProcessA_t)(
	LPCSTR lpApplicationName,
    LPSTR lpCommandLine,
	LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
	BOOL bInheritHandles,
    DWORD dwCreationFlags,
	LPVOID lpEnvironment,
    LPCSTR lpCurrentDirectory,
	LPSTARTUPINFOA lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation
);
```
### VirtualAllocEx
```
typedef LPVOID (WINAPI *VirtualAllocEx_t)(
	HANDLE hProcess,
	LPVOID lpAddress,
	SIZE_T dwSize,
	DWORD  flAllocationType,
	DWORD  flProtect
);
```

### WriteProcessMemory
```
typedef BOOL (WINAPI *WriteProcessMemory_t)(
	HANDLE  hProcess,
	LPVOID  lpBaseAddress,
	LPCVOID lpBuffer,
	SIZE_T  nSize,
	SIZE_T  *lpNumberOfBytesWritten
);
```

### QueueUserAPC
```
typedef DWORD (WINAPI *QueueUserAPC_t)(
    PAPCFUNC pfnAPC,
    HANDLE hThread,
    ULONG_PTR dwData
);
```
### ResumeThread
```
typedef DWORD (WINAPI *ResumeThread_t)(
    HANDLE hThread
);
```