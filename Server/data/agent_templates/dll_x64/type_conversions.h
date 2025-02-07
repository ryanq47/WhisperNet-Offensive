
#ifndef TYPE_CONVERSTIONS_H
#define TYPE_CONVERSTIONS_H

#include <stdlib.h>
#include <windows.h>

char* wchar_to_utf8(const WCHAR* wide_str);
WCHAR* utf8_to_wchar(const char* utf8_str);
char* wchar_to_ansi(const WCHAR* wide_str);
WCHAR* ansi_to_wchar(const char* ansi_str);

#endif
