## Constructs code for binaries
## Meant to be called from binary_models.py, but can be called form anywhere.

# Plan:
#  - Create dir in /tmp, with UUID as name.
#  - _Copy_ loader into this dir.
#  - Copy shellcode into loader. Use .replace() as a macro system
#  - Pass needed values (path of loader) into docker script
#  - Run docker script.

import shutil
import uuid
from pathlib import Path

from modules.log import log

logger = log(__name__)


class Loader:
    def __init__(self, loader_source_code_path, shellcode):
        self.loader_source_code_path = Path(loader_source_code_path)
        self.shellcode = shellcode

        self._shellcode_cleanup()
        logger.debug(f"Loader source code path: {str(loader_source_code_path)}")
        logger.debug(f"Loader shellcode {self.shellcode }")

    def _shellcode_cleanup(self):
        """
        Cleanup shellcode if needed
        """
        # self.shellcode.strip()
        # nuke whitespace, bring it all together like 0x01,0x02,0x03
        self.shellcode = "".join(self.shellcode.split())

    def _size_of_shellcode_bytes(self):
        # Split by commas and strip whitespace
        bytes_list = [byte.strip() for byte in self.shellcode.split(",")]

        # Filter out only valid hex byte representations (that start with '0x' and have exactly 4 characters)
        valid_bytes = [
            byte for byte in bytes_list if byte.startswith("0x") and len(byte) == 4
        ]

        # Return the count of valid bytes
        return len(valid_bytes)

    def construct(self):
        try:
            logger.warning("HACK IMPLEMENTED: ../ in filepath for agents. FIX")
            # Create a unique temp directory
            # will need to clean this up every so often.
            build_context_tmp_dir = Path("_docker/build_tmp") / str(uuid.uuid4())
            build_context_tmp_dir.mkdir(parents=True, exist_ok=True)

            logger.debug(f"Loader being constructed in {str(build_context_tmp_dir)}")

            # Copy the source code to the temp directory
            logger.debug(Path.cwd())
            logger.debug(
                f"Copying {self.loader_source_code_path} to {build_context_tmp_dir}"
            )
            # Copy the entire contents of the source directory to the temp directory
            # Copy the entire contents of the source directory to the build context temp directory
            try:
                shutil.copytree(
                    self.loader_source_code_path,
                    build_context_tmp_dir,
                    dirs_exist_ok=True,
                )
                logger.debug(
                    f"Copied contents of {self.loader_source_code_path} to {build_context_tmp_dir}"
                )
            except Exception as e:
                print(f"Error copying files: {e}")

            main_rs_file = build_context_tmp_dir / "src" / "main.rs"

            logger.debug(f"Looking for main.rs at {str(main_rs_file)}")

            # Read and process the source file to replace the placeholder with shellcode
            with main_rs_file.open("r") as file:
                source_code = file.read()

            # Format the shellcode for Rust as a byte array
            # shellcode_array = (
            #    SHELLCODE  # ", ".join(f"0x{byte:02x}" for byte in self.shellcode)
            # )

            # can change this up later to do a "let shellcode: [whatever]" if needed.
            # for now, it just replaces the current array contents
            shellcode_size = len(self.shellcode)

            processed_code = source_code.replace(
                "SHELLCODE_PLACEHOLDER", f"{self.shellcode}"
            ).replace(
                "SHELLCODE_SIZE_PLACEHOLDER", f"{self._size_of_shellcode_bytes()}"
            )

            # Write the processed code back to the temporary file
            with main_rs_file.open("w") as file:
                file.write(processed_code)

            # Return the path of the modified file
            return build_context_tmp_dir
        except Exception as e:
            logger.error(e)
            raise e


class Dropper:
    ...

    # same as loader, but with IP's n stuff instead of shellcode
