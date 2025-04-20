import time
import logging
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException
)

from app.loggin_config import setup_logging
from app.utils import build_chrome_options, retry


# --- Constants ---
BASE_URL = "https://news.ycombinator.com/?p={}"


def load_hn_page(driver, page: int) -> None:
    try:
        driver.get(BASE_URL.format(page))
        time.sleep(2)
    except Exception:
        raise ConnectionError(
            f"Error reaching {BASE_URL.format(page)}. "
            "Check the internet connection."
        )


def extract_stories(driver) -> List[Dict]:
    stories = []
    items = driver.find_elements(By.CSS_SELECTOR, "tr.athing")
    subtexts = driver.find_elements(By.CSS_SELECTOR, "td.subtext")

    for i in range(len(items)):
        try:
            title_elem = items[i].find_element(
                By.CSS_SELECTOR, "span.titleline a"
            )
            title = title_elem.text
            url = title_elem.get_attribute("href")

            score_elem = subtexts[i].find_element(
                By.CSS_SELECTOR, "span.score"
            )
            score = int(score_elem.text.split()[0])

            stories.append({
                "title": title,
                "url": url,
                "score": score
            })
        except (NoSuchElementException, IndexError):
            logging.debug(
                f"Skipping item {i} due to missing elements."
            )
            continue

    return stories


def go_to_next_page(driver) -> bool:
    try:
        more_link = driver.find_element(By.LINK_TEXT, "More")
        more_link.click()
        time.sleep(2)
        return True
    except NoSuchElementException:
        logging.info("No more pages to scrape.")
        return False


# --- Main Scraper Function ---
@retry(max_attempts=3)
def get_hackernews_top_stories(page: int = 1) -> List[Dict]:
    logging.info("Starting Hacker News Scraping ...")
    driver = None

    try:
        options = build_chrome_options()
        driver = webdriver.Chrome(options=options)

        load_hn_page(driver, page)
        stories = extract_stories(driver)

        # Optionally go to next page (can be extended later)
        go_to_next_page(driver)

        return stories

    except WebDriverException as e:
        logging.critical(f"WebDriver error: {e}")
        raise
    except ConnectionError as e:
        logging.error(str(e))
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Scraping finished and browser closed.")


# --- Entry Point ---
if __name__ == "__main__":
    setup_logging("scrape_hn")

    try:
        top_stories = get_hackernews_top_stories()
        for story in top_stories[:10]:
            print(
                f"Score: {story['score']} | "
                f"{story['title']} | {story['url']}"
            )
    except Exception as e:
        logging.critical(f"Script failed entirely: {e}")
