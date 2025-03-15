'''
For debugging a .dll... this will print any errors to STDOUT. Change the .DLL name in the file plz.

'''

import ctypes

# Load the DLL
my_dll = ctypes.CDLL("C:\\Users\\ryan\Downloads\\test_dll_dll_x64_192.168.212.128_9999.dll")

# Call the function from the DLL
my_dll.Start()
