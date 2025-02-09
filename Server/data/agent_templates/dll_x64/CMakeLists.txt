cmake_minimum_required(VERSION 3.10)
project(AgentC2 LANGUAGES C CXX)

# Set output directory for DLL
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Define source files for AgentC2
set(AGENT_SOURCES
    ${CMAKE_SOURCE_DIR}/core.c
    ${CMAKE_SOURCE_DIR}/cJSON.c
    ${CMAKE_SOURCE_DIR}/type_conversions.c
    ${CMAKE_SOURCE_DIR}/whisper_winapi.c
    ${CMAKE_SOURCE_DIR}/whisper_dynamic_config.c
)

# Ensure headers exist
set(AGENT_HEADERS
    ${CMAKE_SOURCE_DIR}/whisper_config.h
    ${CMAKE_SOURCE_DIR}/whisper_commands.h
    ${CMAKE_SOURCE_DIR}/whisper_json.h
    ${CMAKE_SOURCE_DIR}/whisper_winapi.h
    ${CMAKE_SOURCE_DIR}/type_conversions.h
    ${CMAKE_SOURCE_DIR}/cJSON.h
    ${CMAKE_SOURCE_DIR}/comms_http.h
    ${CMAKE_SOURCE_DIR}/whisper_dynamic_config.h
)

# Check platform
if (WIN32)
    message(STATUS "Compiling for Windows DLL")
    set(WINDOWS_LIBS wininet)
else() # aka cross-compiling for Windows
    message(STATUS "Compiling on Linux (Cross-Compiling for Windows)")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)
    set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++)
endif()

# Create DLL instead of an executable
add_library(agent SHARED ${AGENT_SOURCES})

# Ensure function symbols are exported
set_target_properties(agent PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
)
# Set the output name for the DLL
set_target_properties(agent PROPERTIES OUTPUT_NAME "dll_x64.dll")

# Include necessary directories
target_include_directories(agent PRIVATE ${CMAKE_SOURCE_DIR})

# Link against required Windows libraries
target_link_libraries(agent ${WINDOWS_LIBS})

message(STATUS "CMake configured successfully for AgentC2 DLL.")
