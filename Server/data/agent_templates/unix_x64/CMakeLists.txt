cmake_minimum_required(VERSION 3.10)
project(AgentC2 LANGUAGES C CXX)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Common compile definitions
add_compile_definitions(_CRT_SECURE_NO_WARNINGS)

# Common compile options for Unix x64
add_compile_options(
    -Os                            # Optimize for size
    -fno-stack-protector           # Disable stack protection
    -ffunction-sections            # Place functions in separate sections
    -fdata-sections                # Place data in separate sections
    -flto                          # Enable Link Time Optimization (LTO)
    -Wl,--gc-sections              # Remove unused sections during linking
    -s                             # Strip debug symbols
    -Wall -Wextra                  # Keep warnings for code hygiene
    -m64                           # Ensure 64-bit build (usually the default on x64 systems)
)

# Source & Header Files
set(AGENT_SOURCES
    ${CMAKE_SOURCE_DIR}/core.c
    ${CMAKE_SOURCE_DIR}/cJSON.c

)

set(AGENT_HEADERS
    ${CMAKE_SOURCE_DIR}/whisper_config.h
    ${CMAKE_SOURCE_DIR}/whisper_json.h
    ${CMAKE_SOURCE_DIR}/whisper_commands.h
    ${CMAKE_SOURCE_DIR}/comms_http.h
    ${CMAKE_SOURCE_DIR}/cJSON.h
)

if (UNIX)
    message(STATUS "Compiling natively for Unix x64.")
    # You may add Unix-specific libraries if needed (e.g., pthread)
    # set(UNIX_LIBS pthread)
    # Linker optimizations (already set by compile options, but added here for clarity)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections -s -flto")
endif()

# Build Target
add_executable(agent ${AGENT_SOURCES} ${AGENT_HEADERS})
target_include_directories(agent PRIVATE ${CMAKE_SOURCE_DIR})



# If any Unix-specific libraries are needed, link them here.
find_package(CURL REQUIRED)
target_include_directories(agent PRIVATE ${CURL_INCLUDE_DIRS})
target_link_libraries(agent PRIVATE CURL::libcurl)

# Output Name - 'MACRO_OUTPUT_NAME' gets replaced by build_interface, so the user can specify a name
set_target_properties(agent PROPERTIES OUTPUT_NAME "MACRO_OUTPUT_NAME")

message(STATUS "CMake configured successfully for AgentC2 on Unix x64.")
