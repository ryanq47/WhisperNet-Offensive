import shutil
import pathlib
import subprocess
import os
import threading
from modules.utils import generate_unique_id, generate_mashed_name
from modules.config import Config
from modules.log import log
import random
import importlib
import sys

logger = log(__name__)


class HttpBuildInterface:
    def __init__(
        self, agent_type, callback_address, callback_port, build_script, agent_name=None
    ):
        self.build_id = generate_unique_id()
        self.agent_type = agent_type
        self.callback_address = callback_address
        self.callback_port = callback_port
        self.build_script = build_script  # filename itself

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
        # build script path
        self.build_script_path = self.base_build_path / "scripts" / self.build_script

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
            self.pre_compilation_configuration()  # Placeholder for macro replacement
            self.custom_configure_script()
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

    def pre_compilation_configuration(self):
        """
        For pre-compile adjustments to the agent

        """
        logger.debug("Performing macro replacements.")

        # Dictionary of macros to replace in corresponding files
        # add here for each file name and it'll loop over to replace
        macro_replacements = {
            "CMakeLists.txt": {"MACRO_OUTPUT_NAME": self.binary_name},
            "whisper_config.h": {
                # required
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

    def custom_configure_script(self):

        # HEY! Take passed in confugre script, from .scripts/somename.py, and then name it configure.py before doing this

        # nuke previous config script if exists
        config_path = self.base_build_path / "configure.py"
        if config_path.exists():
            config_path.unlink()

        # copy script out of scripts dir, and copy into base build path, as configure.py, so it runs in the correct location
        shutil.copy(self.build_script_path, self.base_build_path / "configure.py")

        module_path = (
            pathlib.Path(self.base_build_path) / "configure.py"
        )  # Ensure it points to a .py file

        logger.debug(f"Using configure script at: {module_path}")

        # Check if the file exists
        if not module_path.exists():
            logger.debug(f"Error: {module_path} does not exist.")
            return

        # otherwise do dynamic import & call script
        module_path = self.base_build_path / "configure.py"  # path of agent
        mod = load_module_from_path("configure.py", module_path)
        # Dynamically retrieve the "build" class
        ConfigureClass = getattr(mod, "Configure")  # Assuming the class name is "build"
        # Initialize the class with the required arguments
        ConfigureClass = ConfigureClass(self.base_build_path)
        ConfigureClass.configure()

    def cleanup(self):
        try:
            if self.base_build_path.exists():
                logger.debug(f"Cleaning up build directory: {self.base_build_path}")
                shutil.rmtree(self.base_build_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")


def load_module_from_path(module_name, file_path):
    file_path = pathlib.Path(file_path)  # Ensure it's a Path object
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Module file not found: {file_path}")

    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {module_name} from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
