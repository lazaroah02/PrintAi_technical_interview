import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from functools import wraps
from app.loggin_config import setup_logging

# ------------------- Retry Decorator -------------------


def retry(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        logging.error("Max retries reached. Giving up.")
                        raise
        return wrapper
    return decorator

# ------------------- Main Scraper Function -------------------


@retry(max_attempts=3)
def get_hackernews_top_stories(page=1):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")


    BASE_URL = "https://news.ycombinator.com/?p={}"

    driver = None

    try:

        # Using webdriver-manager to manage automatically chromedriver
        driver = webdriver.Chrome(options=options)

        logging.info("Starting Hacker News Scraping ...")

        try:
            driver.get(BASE_URL.format(page))
        except Exception:
            raise ConnectionError()

        time.sleep(2)

        stories = []
        items = driver.find_elements(By.CSS_SELECTOR, 'tr.athing')
        subtexts = driver.find_elements(By.CSS_SELECTOR, 'td.subtext')

        for i in range(len(items)):
            try:
                title_elem = items[i].find_element(
                    By.CSS_SELECTOR, 'span.titleline a')
                title = title_elem.text
                url = title_elem.get_attribute('href')
                score_elem = subtexts[i].find_element(
                    By.CSS_SELECTOR, 'span.score')
                score = int(score_elem.text.split()[0])
            except (NoSuchElementException, IndexError):
                logging.debug(f"Skipping item {i} due to missing elements.")
                continue

            stories.append({
                "title": title,
                "url": url,
                "score": score
            })

        try:
            more_link = driver.find_element(By.LINK_TEXT, "More")
            more_link.click()
            time.sleep(2)
        except NoSuchElementException:
            logging.info("No more pages to scrape.")

        return stories
    except WebDriverException as e:
        logging.critical(f"Failed to start WebDriver: {e}")
        raise
    except ConnectionError:
        raise ConnectionError(
            f"Connection Error: Error reaching {BASE_URL.format(page)}. Check the internet connection")
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        raise

    finally:
        if driver:
            driver.quit()
            logging.info("Scraping finished and browser closed.")


# ------------------- Execution -------------------


if __name__ == "__main__":
    setup_logging("scrape_hn")
    try:
        top_stories = get_hackernews_top_stories()
        for story in top_stories[:10]:
            print(
                f"Score: {story['score']} | {story['title']} | {story['url']}")
    except Exception as e:
        logging.critical(f"Script failed entirely: {e}")
