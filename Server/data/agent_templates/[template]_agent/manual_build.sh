## Manual CMAKE build for testing - This would replace the server work, so this would just need to call the configure script, and then call the cmake commands
## This is meant for debugging, or something on the server breaks

rm -rf ./build

# configure script
#...

# cmake build
mkdir -p build          # Create a separate build directory
cd build                # Enter the build directory
cmake ..                # Configure the project (generate Makefiles, Ninja, or VS project files)
cmake --build .         # Compile the project
