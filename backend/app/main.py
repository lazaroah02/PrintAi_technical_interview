import logging
from flask import Flask, request
from flask_restful import Api, Resource
from app.tasks import scrape_books_task
from app.loggin_config import setup_logging
from app.scraping.scrape_hn import get_hackernews_top_stories
import redis
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
import requests

# --- Config logging ---
setup_logging("app")

# Load .env
load_dotenv()

app = Flask(__name__)
api = Api(app)

#cors config
CORS(app, resources={
    r"/*": {"origins": "*"},
})

class HelloWorld(Resource):
    def get(self):
        return {
            "mensaje": "Welcome!",
            "routes": " /init, /status/<task_id>, /headlines, /books"
        }


class Init(Resource):
    def post(self):
        try:
            task = scrape_books_task.delay()    
            return {
                "message": "Books Scraping Started!",
                "task_id": task.id
            }
        except:
            return {
                "message":"Error starting the task!"
            }, 500


class Headlines(Resource):
    def get(self):
        page = request.args.get('page', 1)
        try:
            stories = get_hackernews_top_stories(page)
            return {
                "message": "Success!",
                "data": stories
            }
        except:
            return {
                "message":"Error getting the news"
            }, 500

class Books(Resource):
    def get(self):
        # Parámetros opcionales
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_value = request.args.get('search', "").lower()
        category = request.args.get('category', "").lower()

        try:
            # Redis connection
            REDIS_HOST = os.getenv("REDIS_HOST", 'redis')
            REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
            REDIS_DB = int(os.getenv("REDIS_DB", 0))
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
            
            # get books keys
            keys = r.keys("book:*")
            books = []

            for key in keys:
                data = r.get(key)
                if data:
                    book = json.loads(data)

                    # Search by title and or category
                    if search_value and search_value not in book['title'].lower():
                        continue
                    if category and category not in book['category'].lower():
                        continue

                    books.append(book)

            # Pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_books = books[start:end]
            
            return {
                "message": "Success",
                "total_books": len(books),
                "page": page,
                "page_size": limit,
                "data": paginated_books
            }

        except Exception as e:
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
            "result": result
        }

class StartInitialBooksScrape(Resource):
    def post(self):
        try:
            logging.info("Fetching current books from /books endpoint...")
            response = requests.get("http://api:5000/books")  

            if response.status_code != 200:
                logging.error(f"Failed to fetch books. Status code: {response.status_code}")
                return {"message": "Failed to fetch books"}, 500

            data = response.json()
            total_books = data.get("total_books", 0)
            logging.info(f"Total books found: {total_books}")

            # If books exist, skip initialization
            if total_books > 0:
                logging.info("Books already present. Skipping initial scrape.")
                return {"message": f"{total_books} books already present. Skipping scraper."}, 200

            # If no books, trigger the scraper
            logging.info("No books found. Triggering scraper via /init...")
            init_response = requests.post("http://api:5000/init")

            if init_response.status_code != 200:
                logging.error(f"Scraper initialization failed. Status code: {init_response.status_code}")
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

