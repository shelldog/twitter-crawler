# Copyright (C) 2022 - Kha Tran

""" Error Handlers source code"""

import sys

from enum import Enum
from logging import Logger
from typing import Union

from rich.console import Console


CONSOLE = Console(file=sys.stderr)


#   ErrorMode inputs
class ErrorMode(Enum):
    Ignore = 0
    NoTrace = 1
    TruncTrace = 2
    FullTrace = 3


# Exit codes for Exception.
ERROR_CODES = {
    "SystemExit": 2,
    "FileNotFoundError": 21,
    "InvalidCsvError": 22,
    "InvalidJsonError": 22,
    "EmptyTxtError": 22,
    "InvalidListError": 22,
    "MissingFieldsError": 23,
    "InsufficientArgs": 24,
    "EmptyCache": 25,
    "CVEDataForYearNotInCache": 26,
    "CVEDataForCurlVersionNotInCache": 27,
    "AttemptedToWriteOutsideCachedir": 28,
    "SHAMismatch": 29,
    "ExtractionFailed": 30,
    "UnknownArchiveType": 31,
    "UnknownConfigType": 32,
    "CVEDataMissing": 33,
    "InvalidCheckerError": 34,
    "NVDRateLimit": 35,
    "InvalidIntermediateJsonError": 36,
    "NVDServiceError": 37,
}


#   Error Handler context manager
class ErrorHandler:

    exit_code: int
    exc_val: Union[BaseException, None]

    def __init__(self, logger: Logger = None, mode: ErrorMode = ErrorMode.TruncTrace) -> None:
        self.logger = logger
        self.mode = mode
        self.exit_code = 0
        self.exc_val = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, BaseException):
            self.exit_code = ERROR_CODES.get(exc_type, -1)
            self.exc_val = exc_val

        if self.mode == ErrorMode.Ignore:
            return True

        if exc_type:
            if self.logger and exc_val:
                self.logger.error(f"{exc_type.__name__}: {exc_val}")
            if self.mode == ErrorMode.NoTrace:
                sys.exit(self.exit_code)
            if self.mode == ErrorMode.TruncTrace:
                CONSOLE.print_exception()
                sys.exit(self.exit_code)
            return False
