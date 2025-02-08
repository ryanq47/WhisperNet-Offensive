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

#ifndef WHISPER_WINAPI_H
#define WHISPER_WINAPI_H

#include <stdio.h>
#include <windows.h>
#include <wininet.h> // Required for HINTERNET functions

// Function to dynamically resolve APIs
FARPROC ResolveFunction(const wchar_t* module_name, const char* function_name);

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

// File I/O
BOOL WhisperReadFile(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead, LPDWORD lpNumberOfBytesRead,
    LPOVERLAPPED lpOverlapped);

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

#endif // WHISPER_WINAPI_H
