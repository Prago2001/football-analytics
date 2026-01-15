from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Literal
import json
import time
import base64
import re
import logging
import atexit
import pandas as pd
from .squads_scraper import dismiss_cookie_banner
from parser.parse_events import EventsDataParser
from parser.parse_stats import StatsParser

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ScrapeMatchData:
    """
    Scrape match data and stats from opta
    ### Example:
        ```
        scraper = ScrapeMatchData(headless=True)
        scraper.scrape()
        scraper.filter_team_data()
        scraper.save_data()
        ```
    """

    def __init__(
        self, headless: bool = True, chrome_exe: str = "/opt/homebrew/bin/chromedriver"
    ):
        """
        Initialize squad scraper

        :param self: Description
        :param headless: Description
        :type headless: bool
        :param chrome_exe: Description
        :type chrome_exe: str
        """
        service = Service(chrome_exe)

        opts = Options()
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        opts.add_experimental_option(
            "perfLoggingPrefs",
            {"enableNetwork": True, "enablePage": False, "traceCategories": "network"},
        )
        opts.add_argument("--start-maximized")
        if headless is True:
            opts.add_argument("--headless=new")
            logger.info("Starting squad scraper in headless mode")
        else:
            logger.info("Starting squad scraper in chrome browser")
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])
        opts.add_argument("--log-level=3")

        atexit.register(self.close_webdriver)
        self.driver = webdriver.Chrome(service=service, options=opts)

    def close_webdriver(self):
        self.driver.quit()

    def capture_data(
        self,
    ):
        """Capture and parse the PerformFeeds squad API response"""
        result = {}
        data_type = ["matchevent", "matchstats"]
        try:
            # Wait for performance logs to be populated
            time.sleep(3)

            logs = self.driver.get_log("performance")
            for entry in logs:
                try:
                    msg = json.loads(entry["message"])
                    message = msg.get("message", {})
                    params = message.get("params", {})

                    if message.get("method") == "Network.responseReceived":
                        response = params.get("response", {})
                        request_id = params.get("requestId")
                        url = response.get("url", "")

                        # Filter for PerformFeeds squad API
                        if "api.performfeeds.com" in url and any(
                            e in url for e in data_type
                        ):
                            status = response.get("status")

                            if status == 200:
                                # Get response body
                                try:
                                    body_info = self.driver.execute_cdp_cmd(
                                        "Network.getResponseBody",
                                        {"requestId": request_id},
                                    )

                                    body = body_info.get("body", "")
                                    is_base64 = body_info.get("base64Encoded", False)

                                    # Decode if base64
                                    if is_base64:
                                        body = base64.b64decode(body).decode(
                                            "utf-8", errors="ignore"
                                        )

                                    # Parse JSONP response
                                    # Format: TM3_..._callback({ ... })
                                    match = re.search(r"\((.*)\);?$", body.strip())

                                    if match:
                                        json_str = match.group(1)
                                        data = json.loads(json_str)

                                        for el in data_type:
                                            if el in url:
                                                logger.info(
                                                    f"Response for {el} found..."
                                                )
                                                result[el] = data

                                except Exception as e:
                                    logger.error(f"Error processing response: {e}")
                                    continue

                except Exception:
                    logger.error(f"Error while filtering network logs: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error capturing squads API: {e}")
        finally:
            return result

    def scrape(
        self,
        match_url: str,
    ):
        logger.info(f"Starting squad scrape process...")
        logger.info(f"Loading page {match_url}")

        self.driver.get(match_url)

        dismiss_cookie_banner(self.driver)

        time.sleep(2)
        try:

            iframe = WebDriverWait(self.driver, 2).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "match-centre-frame"))
            )
            logger.info("iframe located ...")
            a_elem = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "ui-id-2"))
            )
            a_elem.click()
            time.sleep(3)
        except Exception as e:
            logger.error(f"Error while interacting with team stats button: {e}")

        try:
            a_elem = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "ui-id-3"))
            )
            a_elem.click()
            time.sleep(3)

        except Exception as e:
            logger.error(f"Error while interacting with match events button: {e}")

        result = self.capture_data()

        return result.get("matchevent", {}), result.get("matchstats", {})
