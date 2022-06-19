# Copyright (C) 2022 - Kha Tran

""" Crawler source code """

from __future__ import annotations
import profile

from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions

URL: str = "https://cvetrends.com/"


class Crawler:

    # Crawler constructor
    def __init__(self, url: str | None = None, headless: bool = True, enable_javascript: bool = True) -> None:
        self.url: str = url if url is not None else URL
        self.options = FirefoxOptions()
        self.headless: bool = headless
        self.enable_javascript: bool = enable_javascript

        # headless configuration
        if self.headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--enable-javascript")

        self.driver = Firefox(
            options=self.options)

        print(self.driver.capabilities)

    # fetchs to URL
    def fetching_url(self) -> None:
        self.driver.get(self.url)

    def run(self):
        # self.fetching_url()

        # html = self.driver.page_source
        # print(html)
        return


crawler = Crawler()
crawler.run()
