import time
import logging
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from app.utils import retry, build_chrome_options
from app.redis_storage import save_books_into_redis_database
from app.loggin_config import setup_logging
from app.models import ScrapedBook, ScrapingResult


# --- Constants ---
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
DETAIL_URL_PREFIX = "https://books.toscrape.com/catalogue/"
IMAGE_BASE_URL = "https://books.toscrape.com/"


def get_catalog_page(driver, page: int) -> BeautifulSoup:
    try:
        driver.get(BASE_URL.format(page))
        time.sleep(2)
        not_found = driver.find_elements(
            By.XPATH, "//h1[contains(text(), '404 Not Found')]"
        )
        if not_found:
            raise ValueError(f"Page {page} not found.")
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException as e:
        logging.warning(f"Timeout on page {page}")
        raise e


def extract_books_from_page(
    soup: BeautifulSoup, driver, remaining: int
) -> List[ScrapedBook]:
    books = []
    articles = soup.select("article.product_pod")

    for article in articles:
        try:
            title = article.h3.a['title']
            price_str = article.select_one(".price_color").text.strip()[1:]
            price = float(price_str)

            if price > 20:
                continue

            book_url = article.h3.a['href']
            full_url = DETAIL_URL_PREFIX + book_url
            driver.get(full_url)
            time.sleep(1)

            book_soup = BeautifulSoup(driver.page_source, 'html.parser')
            category = book_soup.select(
                "ul.breadcrumb li a"
            )[-1].text.strip()
            img_relative_url = book_soup.select_one(
                "div.item.active img"
            )['src']
            cover_url = IMAGE_BASE_URL + img_relative_url.replace("../", "")

            book = ScrapedBook(
                url=full_url,
                title=title,
                price=price_str,
                category=category,
                image_url=cover_url
            )
            books.append(book)

            if len(books) >= remaining:
                break
        except Exception as e:
            logging.warning(f"Failed to process a book: {e}")

    return books


# --- Main Scraping Function ---
@retry(max_attempts=3)
def scrape_books(limit: int = 100) -> None:
    logging.info("Starting book scraping...")
    driver = None
    all_books = []

    try:
        options = build_chrome_options()
        driver = webdriver.Chrome(options=options)
        page = 1

        while len(all_books) < limit:
            logging.info(f"Scraping page {page}...")
            try:
                soup = get_catalog_page(driver, page)
                books = extract_books_from_page(
                    soup, driver, limit - len(all_books)
                )
                if not books:
                    break
                all_books.extend(books)
                page += 1
            except Exception as e:
                logging.warning(
                    f"Skipping page {page} due to error: {e}"
                )
                break

        logging.info(
            f"Scraping complete. Total books collected: {len(all_books)}"
        )
        result = ScrapingResult(
            total_books=len(all_books),
            books=all_books
        )
        save_books_into_redis_database([book.model_dump() for book in result.books])

    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        raise
    finally:
        if driver:
            driver.quit()
        logging.info("Browser closed.")


# --- Entry Point ---
if __name__ == "__main__":
    setup_logging("scrape_books")
    scrape_books()
