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

# --- Config logging ---
setup_logging("app")

# Load .env
load_dotenv()

app = Flask(__name__)
api = Api(app)


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
        page = request.args.get('page')
        if page is None:
            page = 1
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
            REDIS_HOST = os.getenv("REDIS_HOST")
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



# Endpoints
api.add_resource(HelloWorld, "/")
api.add_resource(Init, "/init")
api.add_resource(Headlines, "/headlines")
api.add_resource(Books, "/books")
api.add_resource(TaskStatus, "/status/<string:task_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

