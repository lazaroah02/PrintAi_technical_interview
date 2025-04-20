from functools import wraps
import logging
from selenium.webdriver.chrome.options import Options
import time


# --- Retry Decorator ---
def retry(max_attempts: int = 3, delay: int = 2):
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


def build_chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return options
