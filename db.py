#   Copyright (C) 2022 - Kha Tran

""" Retrieval access and caching CVE Trend Crawler source code """

from __future__ import annotations

import sqlite3 as lite
import logging
import os
import shutil
import subprocess
import pandas as pd
import matplotlib.ticker as tick
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import date

from Core.tweet_crawl import TwitterCrawler
from Handler.error import ErrorMode
from Util.log import LOGGER
from Util.system import exist_PATH
from Util.version import VERSION

logging.basicConfig(level=logging.DEBUG)

today = date.today()
d1 = today.strftime("%d-%m-%Y")


#   Trend Crawler Database PATH
DB_LOCATION_DEFAULT: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "data")
DB_LOCATION_BACKUP: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "backup")
DB_LOCATION_OLD: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Data", "twitter")
IMAGE_PATH: str = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "Image", str(d1))

DB_NAME: str = "Data.db"
DB_ARCHIVE_TEMPLATE: str = "cve-trend-crawler-{}.json.gz"

sns.set(font_scale=1.4)


def reformat_large_tick_values(tick_val, pos):
    """
    Turns large tick values (in the billions, millions and thousands) such as 4500 into 4.5K and also appropriately turns 4000 into 4K (no zero after the decimal).
    """
    if tick_val >= 1000000000:
        val = round(tick_val/1000000000, 1)
        new_tick_format = '{:}B'.format(val)
    elif tick_val >= 1000000:
        val = round(tick_val/1000000, 1)
        new_tick_format = '{:}M'.format(val)
    elif tick_val >= 1000:
        val = round(tick_val/1000, 1)
        new_tick_format = '{:}K'.format(val)
    elif tick_val < 1000:
        new_tick_format = round(tick_val, 1)
    else:
        new_tick_format = tick_val

    # make new_tick_format into a string value
    new_tick_format = str(new_tick_format)

    # code below will keep 4.5M as is but change values such as 4.0M to 4M since that zero after the decimal isn't needed
    index_of_decimal = new_tick_format.find(".")

    if index_of_decimal != -1:
        value_after_decimal = new_tick_format[index_of_decimal+1]
        if value_after_decimal == "0":
            # remove the 0 after the decimal point since it's not needed
            new_tick_format = new_tick_format[0:index_of_decimal] + \
                new_tick_format[index_of_decimal+2:]

    return new_tick_format


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

        # Crawler setup
        self.twitter_crawler = TwitterCrawler()

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
                description TEXT,
                score INTEGER,
                cvss_version INTEGER,
                cvss_vector TEXT,
                twitter_id TEXT
            )
        """
        tweet_query: str = f"""
            CREATE TABLE IF NOT EXISTS tweet (
                cve_id TEXT,
                id INT,
                link TEXT,
                name TEXT,
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
        self.con.close()
        self.con = None

    # Check database exists
    def db_exists(self) -> None:
        if not exist_PATH(self.db_path):
            LOGGER.info(
                f"[bold yellow]Database file '{DB_NAME}' doesn't exist, start creating a new one.[/]", extra={"markup": True})
            subprocess.run(["sqlite3", f"{self.db_path}", "VACUUM"])
        self.db_table_exists()

    # Process tweet to the database
    def db_tweet_crawling(self) -> None:
        self.db_con()
        self.twitter_crawler.search("CVE-", self.con)
        self.con = None

    def apply_with_pandas(self) -> None:
        self.db_con()

        if not os.path.exists(IMAGE_PATH):
            os.makedirs(IMAGE_PATH)

        cves = pd.read_sql("SELECT * FROM cve", con=self.con)

        ax = cves.cve_id.value_counts().head(10).plot.bar(
            x='programming_language', y='file_count', align='center', legend=False, width=0.8, rot=60, figsize=(7, 5), fontsize=14)
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x() * 1.005,
                        p.get_height() * 1.005), rotation=45, fontsize=12)

        ax.yaxis.set_major_formatter(
            tick.FuncFormatter(reformat_large_tick_values))
        ax.set_xlabel(f"CVE Trend today {d1}")
        ax.set_ylabel("Mentions")
        plt.tight_layout()
        plt.grid()
        plt.savefig(IMAGE_PATH + '/cve-trend-today.PNG')

        cur = self.con.cursor()
        # cur.execute("DROP TABLE cve")
        self.con.commit()
        self.con.close()
        self.con = None

    # Rollback the db_backup in case anything fails
    def rollback_db_backup(self) -> None:
        if exist_PATH(os.path.join(self.db_backup, DB_NAME)):
            self.LOGGER.info("Rolling back the backup to its previous state")

            # Remove the db_dir if existed
            if exist_PATH(self.db_dir):
                shutil.rmtree(self.db_dir)

            # Replace the data with the backup
            shutil.move(self.db_backup, self.db_dir)
