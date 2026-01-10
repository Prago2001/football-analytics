from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import base64
import re
import logging
import atexit
import pprint

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def dismiss_cookie_banner(driver: webdriver.Chrome):
    """Dismiss the Usercentrics cookie banner"""
    try:
        driver.execute_script(
            """
                document.querySelector('aside#usercentrics-cmp-ui')
                        .shadowRoot
                        .querySelector('button[data-action-type="deny"]')
                        .click();
            """
        )
        logger.info("Cookie banner dismissed")
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Could not dismiss cookie banner: {e}")
        return False


class ScrapeSquads:
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

    def capture_squad_api(self):
        """Capture and parse the PerformFeeds squad API response"""
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
                        if "api.performfeeds.com" in url and "squads" in url:
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
                                        squad_data = json.loads(json_str)

                                        return squad_data

                                except Exception as e:
                                    logger.error(f"Error processing response: {e}")
                                    continue

                except Exception:
                    continue

            return None

        except Exception as e:
            logger.error(f"Error capturing squads API: {e}")
            return None

    def click_dropdown(self):
        """Click on the team dropdown button"""
        try:
            dropdown_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "hub-navigation-dropdown-button")
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", dropdown_btn
            )
            time.sleep(0.5)
            dropdown_btn.click()
            logger.info("Teams dropdown clicked")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error while opening teams dropdown: {e}")
            return False

    def get_team_links(self):
        """Get all team links from dropdown"""
        try:
            # Wait for dropdown content to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "hub-navigation-dropdown-content-li")
                )
            )

            # Get all team links
            dropdown_items = self.driver.find_elements(
                By.CLASS_NAME, "hub-navigation-dropdown-content-li"
            )

            teams = []
            for item in dropdown_items:
                try:
                    # Skip the selected item which doesn't have an <a> tag
                    link_elem = item.find_element(By.TAG_NAME, "a")
                    href = link_elem.get_attribute("href")
                    team_name = link_elem.text.strip()
                    teams.append({"name": team_name, "url": href})
                except:
                    # This is the currently selected team
                    pass

            logger.info(f"Found {len(teams)} teams in dropdown")
            return teams

        except Exception as e:
            logger.error(f"Could not get team links from dropdown elements: {e}")
            return []

    def close_webdriver(self):
        self.driver.quit()

    def scrape(
        self,
        initial_page_to_load: str = "https://theanalyst.com/football/team/scm-1/manchester-united/squad",
        initial_team_name: str = "Manchester United",
    ):
        all_teams_data = {}
        logger.info(f"Starting squad scrape process...")
        logger.info(f"Loading page {initial_page_to_load}")

        self.driver.get(initial_page_to_load)

        time.sleep(2)

        dismiss_cookie_banner(self.driver)

        squad_data = self.capture_squad_api()
        if "squad" in squad_data:
            all_teams_data[initial_team_name] = squad_data["squad"]
            logger.info(f"Fetched {initial_team_name}'s squad successfully...")
        else:
            logger.warning(f"squad_data doesn't contain key `squad`")

        if not self.click_dropdown():
            logger.error(f"Could not click on on teams dropdown")
            return

        teams = self.get_team_links()
        if not teams or len(teams) == 0:
            logger.error(f"No teams found in dropdown!")
            return

        for idx, team in enumerate(teams, 1):
            try:
                team_name = team["name"]
                team_url = team["url"]

                logger.info(f"\n[{idx}/{len(teams)}] Processing: {team_name}")
                logger.info(f"  URL: {team_url}")

                # Navigate to team page
                self.driver.get(team_url)
                time.sleep(2)

                squad_data = self.capture_squad_api()
                if "squad" in squad_data:
                    all_teams_data[team_name] = squad_data["squad"]
                    logger.info(f"Fetched {team_name}'s squad successfully...")
                else:
                    logger.warning(
                        f"{team_name}'s squad_data doesn't contain key `squad`"
                    )
            except Exception as e:
                logger.error(f"Error processing {team_name}: {e}")
                continue
        return all_teams_data


if __name__ == "__main__":
    scraper = ScrapeSquads(headless=False)
    team_data = scraper.scrape()
    print(team_data)
