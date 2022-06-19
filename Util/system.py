# Copyright (C) 2022 - Kha Tran

import platform
import os

from Util.log import LOGGER


LINUX: str = "Linux"


def on_linux() -> None:
    if platform.system() != LINUX:
        message = """
            [WARNING]: This project was at first developed for Linux only. 
            You may need to install additional utitlities to use this on
            other operationg systems.
        """
        LOGGER.warning(message)


def exist_PATH(path) -> bool:
    return os.path.exists(path)
