import donut
import pathlib
from modules.log import log
import shutil

logger = log(__name__)


class PayloadToShellcode:
    def __init__(
        self,
        file_to_convert: str,
        shellcode_output_file_name: str,
        architecture: int,
        bypass_options: int,
        auto_stage: bool,
    ) -> None:

        # ------------------------------------------
        # Input Validation
        # ------------------------------------------
        # Validate input types
        if not isinstance(file_to_convert, str):
            raise TypeError("file_to_convert must be a string")
        if not isinstance(shellcode_output_file_name, str):
            raise TypeError("shellcode_output_file_name must be a string")
        if not isinstance(architecture, int):
            raise TypeError("architecture must be an integer")
        if not isinstance(bypass_options, int):
            raise TypeError("bypass_options must be an integer")
        if not isinstance(auto_stage, bool):
            raise TypeError("auto_stage must be an bool")

        # Validate allowed values for architecture and bypass options
        allowed_architectures = (1, 2, 3)  # 1=x86, 2=amd64, 3=x86+amd64 (default)
        if architecture not in allowed_architectures:
            raise ValueError(
                f"architecture must be one of {allowed_architectures} (1=x86, 2=amd64, 3=x86+amd64)"
            )
        allowed_bypass = (
            1,
            2,
            3,
        )  # 1=none, 2=abort on fail, 3=continue on fail (default)
        if bypass_options not in allowed_bypass:
            raise ValueError(
                f"bypass_options must be one of {allowed_bypass} (1=none, 2=abort on fail, 3=continue on fail)"
            )

        # Validate file extension (only .exe, .dll, .vba allowed)
        valid_extensions = (".exe", ".dll", ".vba")
        if not file_to_convert.lower().endswith(valid_extensions):
            raise ValueError(
                f"file_to_convert must have one of the following extensions: {valid_extensions}"
            )
        # ------------------------------------------
        # Set values
        # ------------------------------------------

        self.payload_path = pathlib.Path("data/compiled") / file_to_convert
        if not self.payload_path.exists():
            raise FileNotFoundError(f"Payload file not found: {self.payload_path}")

        self.architecture = architecture
        self.shellcode_output_file_name = (
            f"{shellcode_output_file_name}.bin"  # make sure it ends with .bin
        )
        self.shellcode_output_file_path = (
            pathlib.Path("data/compiled") / self.shellcode_output_file_name
        )
        self.bypass = bypass_options
        self.auto_stage = auto_stage

    def convert(self):
        """
        Convert payload into shellcode and write the output to shellcode_output_file_path.
        Returns the generated shellcode.
        """
        try:
            logger.debug(f"Converting payload into shellcode for {self.payload_path}")
            shellcode = donut.create(
                file=str(self.payload_path),  # File to convert
                arch=self.architecture,  # Target architecture
                bypass=self.bypass,  # Bypass options
                output=str(self.shellcode_output_file_path),  # Output file path
            )
            logger.debug(
                f"Shellcode successfully created at: {self.shellcode_output_file_path}"
            )

            if self.auto_stage:
                self.move_shellcode_to_stage_folder(self.shellcode_output_file_name)

            return shellcode
        except Exception as e:
            logger.error(f"Error creating shellcode: {e}")
            raise

    def move_shellcode_to_stage_folder(self, shellcode_file: str) -> pathlib.Path:
        """
        Copies a shellcode file from the 'data/compiled' folder to the 'data/static' folder.

        Args:
            shellcode_file (str): The name of the shellcode file (e.g., 'shellcode.bin').

        Returns:
            pathlib.Path: The destination path where the shellcode file was copied.

        Raises:
            FileNotFoundError: If the source shellcode file does not exist.
            Exception: If any error occurs during the file copy process.
        """
        # Define source and destination paths.
        source_path = pathlib.Path("data/compiled") / shellcode_file
        dest_folder = pathlib.Path("data/static")
        dest_folder.mkdir(
            parents=True, exist_ok=True
        )  # Create folder if it doesn't exist
        dest_path = dest_folder / shellcode_file

        # Check that the source file exists.
        if not source_path.exists():
            logger.error(f"Shellcode file not found: {source_path}")
            raise FileNotFoundError(f"Shellcode file not found: {source_path}")

        # Try to copy the file.
        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Shellcode file copied from {source_path} to {dest_path}")
        except Exception as e:
            logger.error(f"Error copying shellcode file: {e}")
            raise

        return dest_path
