#include "type_conversions.h"
#include <stdlib.h>
#include <windows.h>

char* wchar_to_utf8(const WCHAR* wide_str)
{
    if (!wide_str)
        return NULL;

    int len = WideCharToMultiByte(CP_UTF8, 0, wide_str, -1, NULL, 0, NULL, NULL);
    if (len <= 0)
        return NULL;

    char* utf8_str = (char*)malloc(len);
    if (!utf8_str)
        return NULL;

    WideCharToMultiByte(CP_UTF8, 0, wide_str, -1, utf8_str, len, NULL, NULL);
    return utf8_str; // Caller must free()
}

WCHAR* utf8_to_wchar(const char* utf8_str)
{
    if (!utf8_str)
        return NULL;

    int len = MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, NULL, 0);
    if (len <= 0)
        return NULL;

    WCHAR* wide_str = (WCHAR*)malloc(len * sizeof(WCHAR));
    if (!wide_str)
        return NULL;

    MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, wide_str, len);
    return wide_str; // Caller must free()
}

char* wchar_to_ansi(const WCHAR* wide_str)
{
    if (!wide_str)
        return NULL;

    int len = WideCharToMultiByte(CP_ACP, 0, wide_str, -1, NULL, 0, NULL, NULL);
    if (len <= 0)
        return NULL;

    char* ansi_str = (char*)malloc(len);
    if (!ansi_str)
        return NULL;

    WideCharToMultiByte(CP_ACP, 0, wide_str, -1, ansi_str, len, NULL, NULL);
    return ansi_str; // Caller must free()
}
WCHAR* ansi_to_wchar(const char* ansi_str)
{
    if (!ansi_str)
        return NULL;

    int len = MultiByteToWideChar(CP_ACP, 0, ansi_str, -1, NULL, 0);
    if (len <= 0)
        return NULL;

    WCHAR* wide_str = (WCHAR*)malloc(len * sizeof(WCHAR));
    if (!wide_str)
        return NULL;

    MultiByteToWideChar(CP_ACP, 0, ansi_str, -1, wide_str, len);
    return wide_str; // Caller must free()
}

// make sure to free after each of these
