# Copyright (C) 2022 - Kha Tran

""" Twitter Crawler arguments source code """

import argparse
import logging
import sys
import textwrap

from typing import ChainMap

from Handler.error import ErrorHandler, ErrorMode
from Util.log import LOGGER
from Util.system import on_linux
from Util.version import VERSION


def main(argv=None) -> None:
    # Parsing the arguments
    argv = argv or sys.argv

    # Reset logger level to INFO
    LOGGER.setLevel(logging.INFO)

    # Take arguments from command line
    parser = argparse.ArgumentParser(
        prog="twitter-crawler",
        description=textwrap.dedent(
            """
                The Twitter Crawler will crawl the top 10 trending vulnerabilities
                on the latest day. 
            """
        )
    )

    # --update | -u
    parser.add_argument("-u", "--update", action="store_true",
                        help="Update the database to the lastest", default=False)

    # Merging into a unique args
    with ErrorHandler(mode=ErrorMode.NoTrace):
        raw_args = parser.parse_args(argv[1:])
        args = {key: value for key, value in vars(raw_args).items() if value}
        defaults = {key: parser.get_default(key) for key in vars(raw_args)}
    args = ChainMap(args, defaults)

    # After arguments has already been parsed, start logging
    LOGGER.info(f"Twitter Crawler v{VERSION}")

    # Checking on Linux OS
    on_linux()


if __name__ == "__main__":
    main()
