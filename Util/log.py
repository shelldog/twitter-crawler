# Copyright (C) 2022

import logging

from rich.logging import RichHandler


# Rich Handler by default Initialize a Console with stderr stream for logs
logging.basicConfig(level="INFO", format="%(name)s - %(message)s",
                    datefmt="[%X]", handlers=[RichHandler()])

# Export the LOGGER globally
LOGGER = logging.getLogger(__package__)
LOGGER.setLevel(logging.INFO)
