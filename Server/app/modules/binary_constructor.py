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

        logger.debug(f"Loader source code path: {str(loader_source_code_path)}")
        logger.debug(f"Loader shellcode {shellcode}")

    def construct(self):
        # Create a unique temp directory
        tmp_dir = Path("/tmp") / str(uuid.uuid4())
        tmp_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Loader being constructed in {str(tmp_dir)}")

        # Copy the source code to the temp directory
        shutil.copy(self.loader_source_code_path, tmp_dir)

        main_rs_file = tmp_dir / "src" / "main.rs"

        logger.debug(f"Looking for main.rs at {str(main_rs_file)}")

        # Read and process the source file to replace the placeholder with shellcode
        with main_rs_file.open("r") as file:
            source_code = file.read()

        # Format the shellcode for Rust as a byte array
        shellcode_array = ", ".join(f"0x{byte:02x}" for byte in self.shellcode)
        processed_code = source_code.replace(
            "SHELLCODE_PLACEHOLDER", f"&[{shellcode_array}]"
        )

        # Write the processed code back to the temporary file
        with main_rs_file.open("w") as file:
            file.write(processed_code)

        # Return the path of the modified file
        return tmp_dir


class Dropper:
    ...

    # same as loader, but with IP's n stuff instead of shellcode
