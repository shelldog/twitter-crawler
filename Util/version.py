# Copyright (C) 2022 - Kha Tran

""" Checks Version of Twitter Crawler """

import textwrap
import requests

from packaging import version

from Util.log import LOGGER


VERSION = "1.0.0"


""" Checks for the latest version available at PyPI """


def check_latest_version():
    name: str = "twitter-crawler"
    url: str = f"https://pypi.org/pypi/{name}/json"

    try:
        res_json = requests.get(url).json()
        crawler_version = res_json["info"]["version"]

        if crawler_version != VERSION:
            LOGGER.info(
                f"[bold red]Warning: You are running version {VERSION} of {name} but the latest PyPI Version is {crawler_version}.[/]",
                extra={"markup": True}
            )

        if version.parse(VERSION) < version.parse(crawler_version):
            LOGGER.info(
                "[bold yellow]Alert: We recommend using the latest stable release.[/]",
                extra={"markup": True}
            )
    except Exception as error:
        LOGGER.warning(
            textwrap.dedent(
                f"""
                    Can't check for the latest version
                    Warning: unable to access 'https://pypi.org/pypi/{name}'
                    Exception details: {error}
                    Please make sure you have a working internet connection or try again later.
                """
            )
        )
