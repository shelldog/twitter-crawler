#   Copyright (C) 2022 - Kha Tran

""" Retrieval access and caching Twitter Crawler source code """

from __future__ import annotations

import sys
import sqlite3 as lite
import logging
import os

from Handler.error import ErrorMode
from Util.log import LOGGER
from Util.system import exist_PATH
from Util.version import VERSION

logging.basicConfig(level=logging.DEBUG)

#   Twitter Crawler Database PATH
DB_LOCATION_DEFAULT: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "data")
DB_LOCATION_BACKUP: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "backup")

DB_NAME: str = "CVE.db"
DB_ARCHIVE_TEMPLATE: str = "twitter-crawler-{}.json.gz"


class Database:

    # Initialize the Database Tables

    DB_DIR: str = DB_LOCATION_DEFAULT
    DB_BACKUP: str = DB_LOCATION_BACKUP
    LOGGER = LOGGER.getChild("Database")
    VERSION: str = VERSION

    # Database class constructor
    def __init__(self, db_dir: str | None = None, db_backup: str | None = None, version_check: bool = False, error_mode: ErrorMode = ErrorMode.TruncTrace) -> None:
        # Database PATH configuration
        self.db_dir: str = db_dir if db_dir is not None else self.DB_DIR
        self.db_backup: str = db_backup if db_backup is not None else self.DB_BACKUP

        # Is checking the verison?
        self.version_check: bool = version_check

        # Error Mode configuration
        self.error_mode: ErrorMode = error_mode

        # Database setup
        self.db_path: str = os.path.join(self.db_dir, DB_NAME)
        self.con: lite.Connection | None = None

        # Check path is existed!
        if not exist_PATH(self.db_path):
            self.rollback_db_backup()

    # Rollback the db_backup in case anything fails
    def rollback_db_backup(self) -> None:
        if exist_PATH(os.path.join(self.db_backup), DB_NAME):
            self.LOGGER.info("")
