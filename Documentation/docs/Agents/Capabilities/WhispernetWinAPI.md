# HCKDWinAPI (`whisper_winapi.h`)

HCKD’s API serves as a wrapper around WinAPI (`windows.h`) functions. By dynamically resolving function addresses at runtime and prefixing all function names with “Whisper,” the API obscures direct references to commonly flagged Windows APIs. This technique enhances OPSEC and may help evade AV/EDR detection.

**Example:**  
```c
// Original Windows API function:
VirtualAllocEx(...);

// HCKD API equivalent:
WhisperVirtualAllocEx(...);
```

---

## Current Capabilities

### Reference Table
| Feature                        | OPSEC Benefit                                         | Supported By... | Notes |
|--------------------------------|------------------------------------------------------|-----------|-----------|
| **Dynamic API Resolution**      | Bypasses IAT-based hooks and static detection methods      | - Standard Agent (DLL, EXE) <br> - ... |... |




### **Dynamic Function Resolution:**  

Dynamic function resolution is a technique used to hide direct API imports from the Import Address Table (IAT) by resolving functions at runtime. This method helps evade static analysis and signature-based detections from antivirus (AV) and Endpoint Detection & Response (EDR) solutions.

NOTE: 
This technique is not effective against behavior-based detection (e.g., advanced EDR solutions that monitor API calls at runtime). However, it has demonstrated success in bypassing signature-based scanners like Windows Defender.


#### How It Works
At the core of this technique is the ResolveFunction function, which dynamically resolves Windows API calls:


```
FARPROC ResolveFunction(const wchar_t* module_name, const char* function_name)
```

#### Step-by-Step Process
 1. Check if the module is already loaded using `GetModuleHandleW`.
 2. If not found, load the module into memory via `LoadLibraryW`.
 3. Find the function’s address dynamically using a custom `GetProcAddress` replacement.

    - Function names are often signatured, so they are XOR-obfuscated before comparison.

---

#### Why XOR the Function Names?

 - When using direct API calls (e.g., `MessageBoxA`), these function names are stored as plaintext in the binary.
 -  Attackers and defenders alike can extract these names using `strings.exe` or static analysis tools.
 - To hide these function names, we apply XOR obfuscation before storing and searching for them.

##### Example
Suppose we want to call `MessageBoxA`. Instead of keeping it as plaintext, we XOR it with a single-byte key (`0x10`):

The XOR'd value is then stored in the binary.

| Function Name  | XOR Key | Obfuscated Output |
|---------------|--------|------------------|
| MessageBoxA   | `0x10`   | `]uccqwuRhQ`    |

At runtime, function names are XOR'd before comparison. If the stored XOR'd name matches the XOR'd function name found in the export table, we retrieve its function pointer dynamically.

---

#### Static Function Pointers for Resolved Functions

Additionally, to avoid resolving the same function multiple times, a static function pointer is used to store the resolved function's address.

Ex:

```
static ResumeThread_t pResumeThread = NULL; //stores the function pointer for future lookups

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
```
#### Why do this?
 - Prevents redundant lookups, makes everything (slightly) more efficient
 - Ensures function resolution only happens once per session.

---

## List of Currently Supported Functions

These `Whisper` functions serve as wrappers around their respective Windows API functions.

Every function listed here supports the following: 

 - Dynamic Function Resolution

| Function Name                 | Windows Equivalent      | Documentation Link |
|-------------------------------|-------------------------|---------------------------------------------------------------------------------------------------------------------|
| `WhisperCreateProcessA`       | `CreateProcessA`        | [CreateProcessA function](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa) |
| `WhisperVirtualAllocEx`       | `VirtualAllocEx`        | [VirtualAllocEx function](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex) |
| `WhisperWriteProcessMemory`   | `WriteProcessMemory`    | [WriteProcessMemory function](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) |
| `WhisperResumeThread`         | `ResumeThread`          | [ResumeThread function](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread) |
| `WhisperGetUserNameW`         | `GetUserNameW`          | [GetUserNameW function](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getusernamew) |
| `WhisperSleep`                | `Sleep`                 | [Sleep function](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleep) |
| `WhisperCreatePipe`           | `CreatePipe`            | [CreatePipe function](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe) |
| `WhisperSetHandleInformation` | `SetHandleInformation`  | [SetHandleInformation function](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-sethandleinformation) |
| `WhisperCloseHandle`          | `CloseHandle`           | [CloseHandle function](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle) |
| `WhisperWaitForSingleObject`  | `WaitForSingleObject`   | [WaitForSingleObject function](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject) |
| `WhisperReadFile`             | `ReadFile`              | [ReadFile function](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile) |
| `WhisperCreateThread`         | `CreateThread`          | [CreateThread function](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread) |
| `WhisperInternetOpenA`        | `InternetOpenA`         | [InternetOpenA function](https://learn.microsoft.com/en-us/windows/win32/api/wininet/nf-wininet-internetopena) |
| `WhisperInternetOpenUrlW`     | `InternetOpenUrlW`      | [InternetOpenUrlW function](https://learn.microsoft.com/en-us/windows/win32/api/wininet/nf-wininet-internetopenurlw) |
| `WhisperInternetReadFile`     | `InternetReadFile`      | [InternetReadFile function](https://learn.microsoft.com/en-us/windows/win32/api/wininet/nf-wininet-internetreadfile) |
| `WhisperInternetCloseHandle`  | `InternetCloseHandle`   | [InternetCloseHandle function](https://learn.microsoft.com/en-us/windows/win32/api/wininet/nf-wininet-internetclosehandle) |
| `WhisperHttpSendRequestA`     | `HttpSendRequestA`      | [HttpSendRequestA function](https://learn.microsoft.com/en-us/windows/win32/api/wininet/nf-wininet-httpsendrequesta) |

