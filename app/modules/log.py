import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class log(logging.Logger):
    def __init__(self, name: str, color: bool = True):
        """
        name (str): Name of logger
        color (bool): Enable colors. Default: True
        """
        # QUick gotcha note, iirc, each logger needs to be a diff name,
        # otherwise it'll start printing multiple times, as multiple handlers get added
        # to the logger of that name

        # init parent logging class
        super().__init__(name)

        self.color = color

        # no longer need basicConfig as we can set this here.
        # basic config is for ONE handler.

        ## add stream handler
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(log_format)
        console.setFormatter(formatter)
        self.addHandler(console)

        # setup file handler to ALSO write to the file
        file_handler = logging.FileHandler("whispernet.log", mode="w")
        # other options: RotatingFileHandler, rotates based on file size.
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))
        self.addHandler(file_handler)

    def debug(self, msg: str, color: str = "", **kwargs):
        super().debug((color if self.color else "") + str(msg) + "\033[0m", **kwargs)

    def info(self, msg: str, color: str = "\033[36m", **kwargs):
        super().info((color if self.color else "") + str(msg) + "\033[0m", **kwargs)

    def warning(self, msg: str, color: str = "\033[33m", **kwargs):
        super().warning((color if self.color else "") + str(msg) + "\033[0m", **kwargs)

    def error(self, msg: str, color: str = "\033[91m", **kwargs):
        super().error((color if self.color else "") + str(msg) + "\033[0m", **kwargs)

    def critical(self, msg: str, color: str = "\033[35m", **kwargs):
        super().critical((color if self.color else "") + str(msg) + "\033[0m", **kwargs)


if __name__ == "__main__":
    log_class = log("testlogger", color=True)
    log_class.info("HIIIIIII")
    log_class.debug("HIIIIIII")
    log_class.warning("HIIIIIII")
    log_class.error("HIIIIIII")
    log_class.critical("HIIIIIII")
