import json
import logging
import os

import redis
import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource
from flasgger import Swagger

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

# Start Swagger
swagger = Swagger(app)


class HelloWorld(Resource):
    def get(self):
        """
        Welcome endpoint with API information.
        ---
        responses:
          200:
            description: Returns a welcome message and the available routes in the API
            schema:
              type: object
              properties:
                mensaje:
                  type: string
                  example: Welcome!
                routes:
                  type: array
                  items:
                    type: object
                    properties:
                      path:
                        type: string
                      description:
                        type: string
        """
        return {
            "mensaje": "Welcome!",
            "routes": [
                {"path": "/", "description": "Welcome endpoint with API information."},
                {"path": "/init", "description": "Start the book scraping task."},
                {"path": "/headlines", "description": "Get Hacker News headlines with optional pagination."},
                {"path": "/books", "description": "Retrieve books information."},
                {"path": "/status/<task_id>", "description": "Check the status of a specific task."},
                {"path": "/start-initial-books-scrape", "description": "Start the initial book scraping process."},
                {"path": "/apidocs", "description": "API documentation."},
            ]
        }


class Init(Resource):
    def post(self):
        """
        Starts the book scraping task.
        ---
        responses:
          200:
            description: Starts the book scraping task
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Books Scraping Started!
                task_id:
                  type: string
                  example: some_task_id
          500:
            description: Error starting the task
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Error starting the task!
        """
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
        """
        Get Hacker News headlines with optional pagination.
        ---
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
            description: Page number for pagination
        responses:
          200:
            description: List of Hacker News top stories
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Success!
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      title:
                        type: string
                        example: Some Hacker News story title
                      url:
                        type: string
                        example: https://news.ycombinator.com/item?id=1234567
          500:
            description: Error retrieving headlines
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Error getting the news
        """
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
        """
        Retrieve books information with pagination and filtering.
        ---
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
            description: Page number for pagination
          - name: limit
            in: query
            type: integer
            default: 10
            description: Number of books per page
          - name: search
            in: query
            type: string
            description: Search term for book title
          - name: category
            in: query
            type: string
            description: Filter books by category
        responses:
          200:
            description: Paginated list of books
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Success
                total_books:
                  type: integer
                  example: 100
                page:
                  type: integer
                  example: 1
                page_size:
                  type: integer
                  example: 10
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      title:
                        type: string
                        example: Book Title
                      author:
                        type: string
                        example: Author Name
                      category:
                        type: string
                        example: Fiction
          500:
            description: Error retrieving books
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Error retrieving books from Redis
        """
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
        """
        Get the status of a specific task.
        ---
        parameters:
          - name: task_id
            in: path
            type: string
            required: true
            description: Task ID for checking its status
        responses:
          200:
            description: Task status and result
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  example: some_task_id
                status:
                  type: string
                  example: SUCCESS
                result:
                  type: string
                  example: Some result message
          500:
            description: Error retrieving task status
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Error retrieving task status
        """
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
        """
        Start the initial book scraping process if no books exist.
        ---
        responses:
          200:
            description: Scraper initialized successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Scraper initialized successfully.
          500:
            description: Error during the scraping process
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: An unexpected error occurred
        """
        try:
            logging.info("Fetching current books from /books endpoint...")
            response = requests.get("http://api:5000/books")

            if response.status_code != 200:
                logging.error("Failed to fetch books.")
                return {"message": "Failed to fetch books"}, 500

            data = response.json()
            total_books = data.get("total_books", 0)
            logging.info(f"Total books found: {total_books}")

            if total_books > 0:
                logging.info("Books already present. Skipping initial scrape.")
                return {
                    "message": f"{total_books} books already present. Skipping scraper."
                }, 200

            logging.info("No books found. Triggering scraper via /init...")
            init_response = requests.post("http://api:5000/init")

            if init_response.status_code != 200:
                logging.error("Scraper initialization failed.")
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
