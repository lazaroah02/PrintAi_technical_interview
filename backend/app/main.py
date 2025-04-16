from flask import Flask, request
from flask_restful import Api, Resource
from app.tasks import scrape_books_task
from app.loggin_config import setup_logging
from app.scraping.scrape_hn import get_hackernews_top_stories

# --- Config logging ---
setup_logging("app")

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {
            "mensaje": "Welcome!",
            "routes": " /init, /status/<task_id>, /headlines"
        }


class Init(Resource):
    def post(self):
        task = scrape_books_task.delay()
        return {
            "message": "Books Scraping Started!",
            "task_id": task.id
        }


class Headlines(Resource):
    def get(self):
        page = request.args.get('page')
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
        page = request.args.get('page')
        search_value = request.args.get('search')
        category = request.args.get('search')
        return {
            "message":"Books"
        }


class TaskStatus(Resource):
    def get(self, task_id):
        from backend.app.tasks import celery
        task = celery.AsyncResult(task_id)
        return {
            "task_id": task.id,
            "status": task.status,
            "result": task.result
        }


# Endpoints
api.add_resource(HelloWorld, "/")
api.add_resource(Init, "/init")
api.add_resource(Headlines, "/headlines")
api.add_resource(TaskStatus, "/status/<string:task_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

