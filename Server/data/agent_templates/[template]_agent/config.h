// =================
// Required Args
// =================

#ifndef CALLBACK_HTTP_HOST
// IP/Hostname of Callback.
#define CALLBACK_HTTP_HOST "MACRO_CALLBACK_ADDRESS"
#endif

#ifndef CALLBACK_HTTP_PORT
// What port to post back to
// Applies to:
#define CALLBACK_HTTP_PORT MACRO_CALLBACK_PORT
#endif


// =================
// Optional Args
// =================

#ifndef MY_VALUE
// What port to post back to
// Applies to:

//CHOOSE 1:
#define MY_VALUE MACRO_MY_VALUE //for build system macro replace, ex in configure script, read file, then .replace(MACRO_MY_VALUE, "somevalue")
// OR
#define MY_VALUE "SOMEVALUE"    //manually specify a value, bypassing configure script

#endif
