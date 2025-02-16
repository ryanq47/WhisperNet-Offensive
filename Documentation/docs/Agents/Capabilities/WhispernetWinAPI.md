# WhisperNetWinAPI (`whisper_winapi.h`)

WhisperNet’s API serves as a wrapper around WinAPI (`windows.h`) functions. By dynamically resolving function addresses at runtime and prefixing all function names with “Whisper,” the API obscures direct references to commonly flagged Windows APIs. This technique enhances OPSEC and may help evade AV/EDR detection (by removing static IAT entries).

> **Example:**  
> ```c
> // Original Windows API function:
> VirtualAllocEx(...);
> 
> // WhisperNet API equivalent:
> WhisperVirtualAllocEx(...);
> ```

---

## Current Capabilities

- **Dynamic Function Resolution:**  

  Removes static imports from the IAT by resolving functions at runtime using `ResolveFunction`. This helps conceal which Windows APIs are used, reducing detection risk by AV/EDR solutions.  
  _Note:_ This technique does not defeat behavior-based detections (e.g. advanced EDRs) but has shown some success against signature-based scanners (such as Windows Defender).

- **Process Creation:**  

  - **Simple:** `WhisperSimpleCreateProcessA` handles basic process creation with minimal parameters.  

  - **Advanced:** `WhisperCreateProcessA` provides full control over process startup details.

- **Memory Management:**  

  - **Memory Allocation:** `WhisperVirtualAllocEx` dynamically allocates memory in a target process.  

  - **Memory Writing:** `WhisperWriteProcessMemory` writes data into a process’s memory space.

- **APC & Thread Manipulation:**  

  Functions like `WhisperQueueUserAPC` and `WhisperResumeThread` allow control over thread execution.

- **Module Loading:**  

  `WhisperLoadLibraryW` loads a DLL into the process’s address space using dynamic resolution.

- **User & System Information:**  

  `WhisperGetUserNameW` retrieves the current user’s name (via Advapi32.dll).

- **Miscellaneous Utilities:**  

  - `WhisperSleep` (pauses execution)  

  - `WhisperCreatePipe` (creates an anonymous pipe)  

  - `WhisperSetHandleInformation` and `WhisperCloseHandle` (handle management)  

  - `WhisperWaitForSingleObject` (object synchronization)  

  - `WhisperReadFile` (file reading)

---

## Type Definitions

The header defines function pointer types for dynamic lookups. For example:

```c
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

typedef LPVOID (WINAPI *VirtualAllocEx_t)(
    HANDLE hProcess,
    LPVOID lpAddress,
    SIZE_T dwSize,
    DWORD  flAllocationType,
    DWORD  flProtect
);

typedef BOOL (WINAPI *WriteProcessMemory_t)(
    HANDLE  hProcess,
    LPVOID  lpBaseAddress,
    LPCVOID lpBuffer,
    SIZE_T  nSize,
    SIZE_T* lpNumberOfBytesWritten
);

typedef DWORD (WINAPI *QueueUserAPC_t)(
    PAPCFUNC pfnAPC,
    HANDLE hThread,
    ULONG_PTR dwData
);

typedef DWORD (WINAPI *ResumeThread_t)(
    HANDLE hThread
);

typedef HMODULE (WINAPI *LoadLibraryW_t)(LPCWSTR);

// Additional typedefs for netapi32 and other APIs are defined similarly.
```

*The complete list is provided in the header file comments.*

---

## Dynamic Function Resolution

At the core of WhisperNet’s stealth is its dynamic resolution technique. The helper function:

```c
FARPROC ResolveFunction(const wchar_t* module_name, const char* function_name);
```

- **How It Works:**  

  1. Attempts to obtain a module handle using `GetModuleHandleW` (which only succeeds if the module is already loaded).  
  2. If that fails, it falls back to `LoadLibraryW` to load the module into memory.  
  3. Finally, it calls `GetProcAddress` to retrieve the address of the desired function.

- **Impact:**  

  Removing static references from the IAT makes it harder for AV/EDR to detect API usage via simple signature scanning.

---

## List of Currently Supported Functions

### Process Creation

#### WhisperSimpleCreateProcessA

```c
int WhisperSimpleCreateProcessA(
    LPCSTR lpApplicationName,
    LPSTR lpCommandLine,
    LPCSTR lpCurrentDirectory
);
```

**Why It Matters:**  

Simplifies process creation by handling the setup (such as initializing `STARTUPINFOA` and `PROCESS_INFORMATION`) for you. Ideal for quickly executing a process without managing detailed attributes.

**How It Works:**  

Internally resolves `CreateProcessA` and calls it with default settings.

**Microsoft Documentation:** [CreateProcessA](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)

**Limitations & Considerations:**  

Offers less control compared to the full version; use only when default settings suffice.

---

#### WhisperCreateProcessA

```c
int WhisperCreateProcessA(
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

**Why It Matters:**  

Provides full control over process creation parameters.

**How It Works:**  

Dynamically resolves `CreateProcessA` and passes all arguments directly to it.

**Microsoft Documentation:** [CreateProcessA](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)

**Limitations & Considerations:**  

Ensure proper initialization of `STARTUPINFOA` and `PROCESS_INFORMATION` before use.

---

### Memory Management

#### WhisperVirtualAllocEx

```c
LPVOID WhisperVirtualAllocEx(
    HANDLE hProcess,
    LPVOID lpAddress,
    SIZE_T dwSize,
    DWORD flAllocationType,
    DWORD flProtect
);
```

**Why It Matters:**  

Allocates memory in the address space of a target process while obscuring the direct API call.

**How It Works:**  

Resolves `VirtualAllocEx` dynamically and invokes it with the provided parameters.

**Microsoft Documentation:** [VirtualAllocEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex)

**Limitations & Considerations:**  

May fail if the target process does not allow the specified allocation; any errors are logged.

---

#### WhisperWriteProcessMemory

```c
BOOL WhisperWriteProcessMemory(
    HANDLE hProcess,
    LPVOID lpBaseAddress,
    LPCVOID lpBuffer,
    SIZE_T nSize,
    SIZE_T* lpNumberOfBytesWritten
);
```

**Why It Matters:**  

Enables writing data into a process’s memory—a common step in code injection or process manipulation.

**How It Works:**  

Dynamically resolves `WriteProcessMemory` and writes the buffer into the target process.

**Microsoft Documentation:** [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)

**Limitations & Considerations:**  

Requires appropriate privileges and memory permissions on the target process.

---

### APC & Thread Manipulation

#### WhisperQueueUserAPC

```c
DWORD WhisperQueueUserAPC(
    PAPCFUNC pfnAPC,
    HANDLE hThread,
    ULONG_PTR dwData
);
```

**Why It Matters:**  

Queues an Asynchronous Procedure Call (APC) for a target thread, useful in process injection techniques.

**How It Works:**  

Resolves `QueueUserAPC` dynamically and queues the APC for execution when the thread becomes alertable.

**Microsoft Documentation:** [QueueUserAPC](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)

**Limitations & Considerations:**  

The APC will not execute until the target thread enters an alertable state.

---

#### WhisperResumeThread

```c
DWORD WhisperResumeThread(
    HANDLE hThread
);
```

**Why It Matters:**  

Resumes a suspended thread—commonly used in process injection or APC techniques.

**How It Works:**  

Dynamically resolves `ResumeThread` and resumes the target thread.

**Microsoft Documentation:** [ResumeThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread)

**Limitations & Considerations:**  

A return value of `-1` indicates an error, with details available via `GetLastError()`.

---

### Module Loading

#### WhisperLoadLibraryW

```c
HMODULE WhisperLoadLibraryW(
    LPCWSTR lpLibFileName
);
```

**Why It Matters:**  

Dynamically loads a DLL into the process’s address space, which can be used to access additional APIs not loaded by default.

**How It Works:**  

Uses dynamic resolution to locate and call `LoadLibraryW`.

**Microsoft Documentation:** [LoadLibraryW](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw)

**Limitations & Considerations:**  

Loading libraries from disk may trigger additional AV/EDR alerts.

---

### User & System Information

#### WhisperGetUserNameW

```c
BOOL WhisperGetUserNameW(
    LPWSTR lpBuffer,
    LPDWORD pcbBuffer
);
```

**Why It Matters:**  

Retrieves the current user’s name, useful for user enumeration or context-specific operations.

**How It Works:**  

Dynamically resolves `GetUserNameW` (from Advapi32.dll) and populates the provided buffer.

**Microsoft Documentation:** [GetUserNameW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getusernamew)

**Limitations & Considerations:**  

Ensure that the buffer is sufficiently sized; otherwise, the call may fail.

---

### Miscellaneous Functions

#### WhisperSleep

```c
void WhisperSleep(
    DWORD dwMilliseconds
);
```

**Why It Matters:**  

Pauses execution for a specified time period, which can be useful for timing operations or delaying actions.

**How It Works:**  

Dynamically resolves and calls `Sleep` from kernel32.dll.

**Microsoft Documentation:** [Sleep](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleep)

**Limitations & Considerations:**  

There is no return value; ensure that the duration is appropriate for your scenario.

---

#### WhisperCreatePipe

```c
BOOL WhisperCreatePipe(
    PHANDLE hReadPipe,
    PHANDLE hWritePipe,
    LPSECURITY_ATTRIBUTES lpPipeAttributes,
    DWORD nSize
);
```

**Why It Matters:**  

Creates an anonymous pipe for interprocess communication.

**How It Works:**  

Dynamically resolves `CreatePipe` and creates both read and write handles.

**Microsoft Documentation:** [CreatePipe](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe)

**Limitations & Considerations:**  

Failures are logged via `GetLastError()` if pipe creation fails.

---

#### WhisperSetHandleInformation

```c
BOOL WhisperSetHandleInformation(
    HANDLE hObject,
    DWORD dwMask,
    DWORD dwFlags
);
```

**Why It Matters:**  

Configures specific properties of an object handle (e.g., marking it as non-inheritable).

**How It Works:**  

Dynamically resolves `SetHandleInformation` and applies the desired settings to the handle.

**Microsoft Documentation:** [SetHandleInformation](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-sethandleinformation)

**Limitations & Considerations:**  

Incorrect flag values or masks may result in errors.

---

#### WhisperCloseHandle

```c
BOOL WhisperCloseHandle(
    HANDLE hObject
);
```

**Why It Matters:**  

Closes open handles to free system resources.

**How It Works:**  

Dynamically resolves `CloseHandle` and closes the specified handle.

**Microsoft Documentation:** [CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle)

**Limitations & Considerations:**  

Ensure that the handle is valid and not in use elsewhere.

---

#### WhisperWaitForSingleObject

```c
DWORD WhisperWaitForSingleObject(
    HANDLE hHandle,
    DWORD dwMilliseconds
);
```

**Why It Matters:**  

Waits for an object (such as a process or thread) to reach a signaled state.

**How It Works:**  

Resolves `WaitForSingleObject` dynamically and waits based on the specified timeout.

**Microsoft Documentation:** [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)

**Limitations & Considerations:**  

Choose timeout values carefully to avoid indefinite waiting or premature timeouts.

---

#### WhisperReadFile

```c
BOOL WhisperReadFile(
    HANDLE hFile,
    LPVOID lpBuffer,
    DWORD nNumberOfBytesToRead,
    LPDWORD lpNumberOfBytesRead,
    LPOVERLAPPED lpOverLapped
);
```

**Why It Matters:**  

Reads data from a file handle—useful for retrieving file contents or data from a pipe.

**How It Works:**  

Dynamically resolves `ReadFile` and attempts to read the specified amount of data.

**Microsoft Documentation:** [ReadFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile)

**Limitations & Considerations:**  

Errors are reported via `GetLastError()` if the read operation fails.

---
