import json
import logging
import os

import redis
import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource

from app.loggin_config import setup_logging
from app.scraping.scrape_hn import get_hackernews_top_stories
from app.tasks import scrape_books_task

# --- Config logging ---
setup_logging("app")

# Load .env
load_dotenv()

app = Flask(__name__)
api = Api(app)

# CORS config
CORS(app, resources={r"/*": {"origins": "*"}})


class HelloWorld(Resource):
    def get(self):
        return {
            "mensaje": "Welcome!",
            "routes": [
                {
                    "path": "/",
                    "description": "Welcome endpoint with API information.",
                },
                {
                    "path": "/init",
                    "description": "Start the book scraping task.",
                },
                {
                    "path": "/headlines",
                    "description": (
                        "Get Hacker News headlines with optional pagination."
                    ),
                },
                {
                    "path": "/books",
                    "description": "Retrieve books information.",
                },
                {
                    "path": "/status/<task_id>",
                    "description": "Check the status of a specific task.",
                },
                {
                    "path": "/start-initial-books-scrape",
                    "description": (
                        "Start the initial book scraping process."
                    ),
                },
            ],
        }


class Init(Resource):
    def post(self):
        try:
            task = scrape_books_task.delay()
            return {
                "message": "Books Scraping Started!",
                "task_id": task.id,
            }
        except Exception:
            return {
                "message": "Error starting the task!",
            }, 500


class Headlines(Resource):
    def get(self):
        page = request.args.get("page", 1)
        try:
            stories = get_hackernews_top_stories(page)
            return {
                "message": "Success!",
                "data": stories,
            }
        except Exception:
            return {
                "message": "Error getting the news",
            }, 500


class Books(Resource):
    def get(self):
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        search = request.args.get("search", "").lower()
        category = request.args.get("category", "").lower()

        try:
            redis_host = os.getenv("REDIS_HOST", "redis")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))
            r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

            keys = r.keys("book:*")
            books = []

            for key in keys:
                data = r.get(key)
                if data:
                    book = json.loads(data)

                    if search and search not in book["title"].lower():
                        continue
                    if category and category not in book["category"].lower():
                        continue

                    books.append(book)

            start = (page - 1) * limit
            end = start + limit
            paginated_books = books[start:end]

            return {
                "message": "Success",
                "total_books": len(books),
                "page": page,
                "page_size": limit,
                "data": paginated_books,
            }

        except Exception:
            return {
                "message": "Error retrieving books from Redis",
            }, 500


class TaskStatus(Resource):
    def get(self, task_id):
        from app.tasks import celery

        task = celery.AsyncResult(task_id)
        result = task.result

        if isinstance(result, BaseException):
            result = str(result)

        return {
            "task_id": task.id,
            "status": task.status,
            "result": result,
        }


class StartInitialBooksScrape(Resource):
    def post(self):
        try:
            logging.info("Fetching current books from /books endpoint...")
            response = requests.get("http://api:5000/books")

            if response.status_code != 200:
                logging.error(
                    "Failed to fetch books. "
                    f"Status code: {response.status_code}"
                )
                return {"message": "Failed to fetch books"}, 500

            data = response.json()
            total_books = data.get("total_books", 0)
            logging.info(f"Total books found: {total_books}")

            if total_books > 0:
                logging.info("Books already present. Skipping initial scrape.")
                return {
                    "message": (
                        f"{total_books} books already present. "
                        "Skipping scraper."
                    )
                }, 200

            logging.info("No books found. Triggering scraper via /init...")
            init_response = requests.post("http://api:5000/init")

            if init_response.status_code != 200:
                logging.error(
                    "Scraper initialization failed. "
                    f"Status code: {init_response.status_code}"
                )
                return {"message": "Failed to initialize scraper."}, 500

            logging.info("Scraper initialized successfully.")
            return {"message": "No books found. Scraper initialized."}, 200

        except Exception as e:
            logging.error(f"Unexpected error during scraping: {e}")
            return {"message": "An unexpected error occurred"}, 500


# Endpoints
api.add_resource(HelloWorld, "/")
api.add_resource(Init, "/init")
api.add_resource(Headlines, "/headlines")
api.add_resource(Books, "/books")
api.add_resource(TaskStatus, "/status/<string:task_id>")
api.add_resource(StartInitialBooksScrape, "/start-initial-books-scrape")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
