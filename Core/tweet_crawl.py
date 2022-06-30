# Copyright (C) 2022 - Kha Tran

""" Crawler source code """

from __future__ import annotations

from fuzzywuzzy import process
import json
import tweepy
import requests

from config import API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from Util.log import LOGGER


NVD_API = "https://services.nvd.nist.gov/rest/json/cve/1.0/{}?addOns=dictionaryCpes"


class TwitterCrawler:

    def __init__(self, api_key: str | None = None, api_secret: str | None = None, access_token: str | None = None, access_token_secret: str | None = None, wait_on_rate_limit: bool | None = False) -> None:
        # cofigure the Authentication
        self.api_key: str = api_key if api_key is not None else API_KEY
        self.api_secret: str = api_secret if api_secret is not None else API_KEY_SECRET
        self.access_token: str = access_token if access_token is not None else ACCESS_TOKEN
        self.access_token_secret: str = access_token_secret if access_token is not None else ACCESS_TOKEN_SECRET
        self.auth = tweepy.OAuth1UserHandler(
            API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )

        # bootstrap the API
        self.api = tweepy.API(self.auth, wait_on_rate_limit=wait_on_rate_limit)

        # The cve list
        self.cves = []

    def is_integer(self, val):
        try:
            int(val)
            return True
        except:
            return False

    # Split the CVE_ID string.
    def split_the_CVE_ID(self, raw_cve):
        y = 0
        format = "CVE-"
        enable = False
        res = "CVE-"

        for i in raw_cve:
            if enable == True:
                if self.is_integer(i):
                    res += i
                elif i == "-":
                    res += i
                else:
                    break
            else:
                if y == 3:
                    enable = True
                if i == format[y]:
                    y += 1
                else:
                    y = 0

        return res

    def get_cve_id(self, content):
        splits = content.split(" ")
        ratio = process.extract("CVE-", splits)

        raw_cve = ""
        for i in ratio:
            if "CVE-" in i[0]:
                raw_cve = i[0]
                break

        # Loc's credit [Deprecated]
        # new_raw = raw_cve.replace("\n", "").strip("()\/#@\"")
        if raw_cve:
            return self.split_the_CVE_ID(raw_cve)

    def insert_database(self, data, db):

        query = """
            INSERT INTO cve (
                cve_id,
                description,
                score,
                cvss_version,
                cvss_vector
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?
            )
        """
        cur = db.cursor()

        cur.execute(
            query,
            [
                data["id"],
                data["description"],
                data["score"],
                data["cvss_version"],
                data["cvss_vector"]
            ]
        )

    def fetch_cve(self, cve_id, data, db):

        res = requests.get(NVD_API.format(cve_id))

        if res.status_code == 200:
            data = res.json()

            package = {
                "id": cve_id,
                "description": data["result"]["CVE_Items"][0]["cve"]["description"]["description_data"][0]["value"],
                "score": "unknown",
                "cvss_version": "unknown",
                "cvss_vector": "unknown"
            }

            base_cve = data["result"]["CVE_Items"][0]["impact"]

            if "baseMetricV3" in base_cve:
                cvssv3 = base_cve["baseMetricV3"]["cvssV3"]
                package["score"] = cvssv3["baseScore"]
                package["cvss_version"] = cvssv3["version"]
                package["cvss_vector"] = cvssv3["vectorString"]
            if "baseMetricV2" in base_cve:
                cvssv2 = base_cve["baseMetricV2"]["cvssV2"]
                package["score"] = cvssv2["baseScore"]
                package["cvss_version"] = cvssv2["version"]
                package["cvss_vector"] = cvssv2["vectorString"]

            self.insert_database(package, db)

    def data_extract(self, data, db):
        cve_id = self.get_cve_id(data.full_text)

        if cve_id is not None:
            """
            print(f"https://twitter.com/tweet/status/{data.id}")
            print(data.user.name)
            print(data.created_at)
            """
            self.fetch_cve(cve_id, data, db)

    def search(self, search_suit, db) -> None:
        for tweet_info in tweepy.Cursor(self.api.search_tweets, q=search_suit, result_type="recent", lang="en", tweet_mode="extended").items(100):

            if "retweeted_status" in dir(tweet_info):
                tweet = tweet_info.retweeted_status
            else:
                tweet = tweet_info

            self.data_extract(tweet, db)
        LOGGER.info("Fetched from twitter to database successfully!")
        db.commit()
        db.close()
