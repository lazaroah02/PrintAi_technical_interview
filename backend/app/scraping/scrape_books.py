import time
import logging
import json
import redis
import hashlib
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
from app.loggin_config import setup_logging


# --- Retry Decorator ---
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


@retry(max_attempts=3)
def scrape_books(books_limit=100):
    # chromedriver
    options = Options()
    options.add_argument("--headless")  # Hide browser window
    options.add_argument("--disable-gpu")  # Optional: improve compatibility
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    driver = None

    BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
    PAGE_URL = "https://books.toscrape.com/catalogue/"
    books_data = []
    page = 1

    try:
        driver = webdriver.Chrome(options=options)
        while len(books_data) < books_limit:
            logging.info(f"Scraping page {page}...")
            try:
                driver.get(BASE_URL.format(page))
                time.sleep(2)  # Wait for the content to load
            except TimeoutException:
                logging.warning(f"Timeout on page {page}")
                break

            # handle not found message
            not_found = driver.find_elements(
                By.XPATH, "//h1[contains(text(), '404 Not Found')]")
            if not_found:
                logging.info(f"Page {page} Not Found")
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.select("article.product_pod")

            for article in articles:
                try:
                    # Title
                    title = article.h3.a['title']

                    # Price
                    price = article.select_one(".price_color").text.strip()[
                        1:]  # price without coin symbol

                    # filter books with price over 20
                    if float(price) > 20:
                        continue

                    # Book detail url to get category and front page
                    book_url = article.h3.a['href']
                    full_book_url = PAGE_URL + book_url
                    driver.get(full_book_url)
                    time.sleep(1)

                    book_soup = BeautifulSoup(
                        driver.page_source, 'html.parser')

                    # Category
                    category = book_soup.select(
                        "ul.breadcrumb li a")[-1].text.strip()

                    # Front Page
                    img_relative_url = book_soup.select_one(
                        "div.item.active img")['src']
                    cover_url = "https://books.toscrape.com/" + \
                        img_relative_url.replace("../", "")

                    # Save Data
                    books_data.append({
                        "url": book_url,
                        "title": title,
                        "price": price,
                        "category": category,
                        "image_url": cover_url
                    })

                    if len(books_data) >= books_limit:
                        break

                    # Back to catalog
                    driver.back()

                except Exception as e:
                    logging.warning(f"Failed to process a book: {e}")

            page += 1
    except WebDriverException as e:
        logging.critical(f"Failed to start WebDriver: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        raise
    finally:
        driver.quit()
        logging.info("Browser closed.")

    # save into redis
    save_into_redis_database(books_data)

    logging.info("Scraping finished.")


def save_into_redis_database(books_data):
    # redis database connection
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        for book in books_data:
            book_id = hashlib.md5(book['url'].encode('utf-8')).hexdigest()
            redis_key = f"book:{book_id}"
            r.set(redis_key, json.dumps(book, ensure_ascii=False))
        logging.info(f"Stored {len(books_data)} books into Redis.")
    except Exception as e:
        logging.error(f"Failed to store data in Redis: {e}")


if __name__ == "__main__":
    setup_logging("scrape_books")
    scrape_books()
