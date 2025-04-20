import hashlib
import os
import json
from typing import Dict, List
from dotenv import load_dotenv
import redis
import logging


def save_books_into_redis_database(books_data: List[Dict]) -> None:
    try:
        load_dotenv()
        REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        REDIS_DB = int(os.getenv("REDIS_DB", 0))
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

        for book in books_data:
            book_id = hashlib.md5(book['url'].encode('utf-8')).hexdigest()
            redis_key = f"book:{book_id}"
            r.set(redis_key, json.dumps(book, ensure_ascii=False))

        logging.info(f"Stored {len(books_data)} books into Redis.")
    except Exception as e:
        logging.error(f"Failed to store data in Redis: {e}")
        raise
