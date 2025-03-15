## Build File, for agent specific build items
import random
import os
import logging

"""
Individual Patch Script for binary

TLDR: Use this for custom edits on the binary at build. If this file is present, it will
call the Configure class, init it, and call the .build() method.

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

        # some function to configure the build/binary

        self.myfunc()

    def myfunc(self):
        with open(self.config_file, "r") as config_h_file:
            print(config_h_file.read())
