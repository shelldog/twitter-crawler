#   Copyright (C) 2022 - Kha Tran

""" Retrieval access and caching Twitter Crawler source code """

from __future__ import annotations
from multiprocessing.dummy import Array


import sqlite3 as lite
import logging
import os
import shutil
import subprocess

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
DB_LOCATION_OLD: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "twitter")

DB_NAME: str = "Data.db"
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

    # Connects the database with SQLITE3
    def db_con(self):
        if not self.con:
            self.con = lite.connect(self.db_path)

    # Bootstraps the Database for storing Twitter CVE later
    def db_bootstrap(self) -> None:
        self.db_con()

    # Check the Table exists
    def db_table_exists(self) -> None:
        self.db_con()
        cursor = self.con.cursor()
        cve_query: str = f"""
            CREATE TABLE IF NOT EXISTS cve (
                cve_id TEXT,
                severity TEXT,
                description TEXT,
                score INTEGER,
                cvss_version INTEGER,
                cvss_vector TEXT,
                PRIMARY KEY(cve_id)
            )
        """
        tweet_query: str = f"""
            CREATE TABLE IF NOT EXISTS tweet (
                cve_id TEXT,
                link TEXT,
                name TEXT,
                subtle TEXT,
                content TEXT,
                retweet INT,
                like INT,
                date_and_time TEXT,
                keyword TEXT,
                FOREIGN KEY(cve_id) REFERENCES cve(cve_id)
            ) 
        """
        cursor.execute(cve_query)
        cursor.execute(tweet_query)
        self.con.commit()

    # Check database exists
    def db_exists(self) -> None:
        if not exist_PATH(self.db_path):
            LOGGER.info(
                f"[bold yellow]Database file '{DB_NAME}' doesn't exist, start creating a new one.[/]", extra={"markup": True})
            subprocess.run(["sqlite3", f"{self.db_path}", "VACUUM"])
        self.db_table_exists()

    # Rollback the db_backup in case anything fails
    def rollback_db_backup(self) -> None:
        if exist_PATH(os.path.join(self.db_backup, DB_NAME)):
            self.LOGGER.info("Rolling back the backup to its previous state")

            # Remove the db_dir if existed
            if exist_PATH(self.db_dir):
                shutil.rmtree(self.db_dir)

            # Replace the data with the backup
            shutil.move(self.db_backup, self.db_dir)
