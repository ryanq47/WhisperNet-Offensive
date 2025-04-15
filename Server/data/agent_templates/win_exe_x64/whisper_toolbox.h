/*
A "toolbox" or set of functions that are meant to make stuff easier, but not meant as direct commands
*/

// void logon_user_with_password() {

// }
#include <windows.h>

char *get_user_from_current_token(void);
char *username_to_sid(const char *username);
char *get_current_token_sid(void);
char *get_user_from_sid_str(const char *sidString);
// char *get_user_from_binary_sid(PSID pSid);
int set_thread_token(HANDLE hImpersonationToken);
char *get_env(const char *varname);