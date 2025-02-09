cmake_minimum_required(VERSION 3.10)
project(AgentC2_DLL LANGUAGES C CXX)

# Ensure output directory exists
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Apply output directories globally for all build types
foreach(OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG_UPPER)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_BINARY_DIR}/bin)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_BINARY_DIR}/bin)
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_BINARY_DIR}/bin)
endforeach()

# Default output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Common compiler definitions
add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
add_compile_options(-DWIN32_LEAN_AND_MEAN -D_CALLCONV=__stdcall -Wall -Wextra -O2)

# Source and header files
set(DLL_SOURCES
    ${CMAKE_SOURCE_DIR}/core.c
    ${CMAKE_SOURCE_DIR}/cJSON.c
    ${CMAKE_SOURCE_DIR}/type_conversions.c
    ${CMAKE_SOURCE_DIR}/whisper_winapi.c
    ${CMAKE_SOURCE_DIR}/whisper_dynamic_config.c
)

set(DLL_HEADERS
    ${CMAKE_SOURCE_DIR}/whisper_config.h
    ${CMAKE_SOURCE_DIR}/whisper_commands.h
    ${CMAKE_SOURCE_DIR}/whisper_json.h
    ${CMAKE_SOURCE_DIR}/whisper_winapi.h
    ${CMAKE_SOURCE_DIR}/type_conversions.h
    ${CMAKE_SOURCE_DIR}/cJSON.h
    ${CMAKE_SOURCE_DIR}/comms_http.h
    ${CMAKE_SOURCE_DIR}/whisper_dynamic_config.h
)

# Platform-specific configurations
if (WIN32)
    message(STATUS "Compiling natively for Windows.")
    set(WINDOWS_LIBS wininet ws2_32 kernel32 user32 advapi32)
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

    set(WINDOWS_LIBS -lwininet -lws2_32 -lkernel32 -luser32 -ladvapi32)
endif()

# Build the DLL
add_library(agent_dll SHARED ${DLL_SOURCES} ${DLL_HEADERS})
target_include_directories(agent_dll PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(agent_dll ${WINDOWS_LIBS})

# DLL-specific properties
set_target_properties(agent_dll PROPERTIES
    OUTPUT_NAME "MACRO_OUTPUT_NAME"
    PREFIX ""                      # No 'lib' prefix for Windows DLL
    SUFFIX ".dll"                  # Ensure .dll extension
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

message(STATUS "CMake configured successfully for AgentC2 DLL.")
