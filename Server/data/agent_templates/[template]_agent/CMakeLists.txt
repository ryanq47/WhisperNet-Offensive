﻿cmake_minimum_required(VERSION 3.10)
project(AgentC2 LANGUAGES C CXX)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Common compile definitions
# basically, these allow strcpy_s instead of like strncpy... cuz im dumb and didn't use POSIX funcs
add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
add_compile_options(
    -DWIN32_LEAN_AND_MEAN          # Reduce Windows headers bloat
    -D_CALLCONV=__stdcall          # Calling convention optimization
    -Os                            # Optimize for size
    -fno-stack-protector           # Disable stack protection - somewhat fine. Disables canaries
    -ffunction-sections            # Place functions in separate sections
    -fdata-sections                # Place data in separate sections
    -flto                          # Enable Link Time Optimization (LTO)
    -Wl,--gc-sections              # Remove unused sections during linking
    -s                             # Strip debug symbols
    -Wall -Wextra                  # Keep warnings for code hygiene
)

# Source & Header Files
set(AGENT_SOURCES
    ${CMAKE_SOURCE_DIR}/core.c
)

set(AGENT_HEADERS
    ${CMAKE_SOURCE_DIR}/config.h
)

# Platform-specific settings
if (WIN32)
    message(STATUS "Compiling natively for Windows.")

    # just some common windows libs
    set(WINDOWS_LIBS wininet ws2_32 kernel32 user32 advapi32)

    # Linker optimizations
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /OPT:REF /OPT:ICF /LTCG")
else()
    message(STATUS "Cross-compiling for Windows from Linux.")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)
    set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++)
    set(CMAKE_RC_COMPILER x86_64-w64-mingw32-windres)

    set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32)
    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

    # just some common windows libs
    set(WINDOWS_LIBS -lwininet -lws2_32 -lkernel32 -luser32 -ladvapi32)

    # Linker optimizations
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--gc-sections -s -flto")


endif()

# Build Target
add_executable(agent ${AGENT_SOURCES} ${AGENT_HEADERS})
target_include_directories(agent PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(agent ${WINDOWS_LIBS})

# Output Name - 'MACRO_OUTPUT_NAME' gets replaced by build_interface, aka automatically, so the user can put in a name
set_target_properties(agent PROPERTIES OUTPUT_NAME "MACRO_OUTPUT_NAME")

message(STATUS "CMake configured successfully for AgentC2.")
