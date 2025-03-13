// core, simple with basic control flow.
#include <stdio.h>
#include "config.h"

int main() {
    printf("Hi!");
    //use values from config.h as macros
    printf("Value from config file: %s", MY_VALUE);
}

