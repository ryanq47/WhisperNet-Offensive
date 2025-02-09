import shutil
import pathlib
import subprocess
import os
import threading
from modules.utils import generate_unique_id, generate_mashed_name
from modules.config import Config
from modules.log import log

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

    def cleanup(self):
        try:
            if self.base_build_path.exists():
                logger.debug(f"Cleaning up build directory: {self.base_build_path}")
                shutil.rmtree(self.base_build_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
