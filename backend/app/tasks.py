from celery import Celery
from app.scraping.scrape_books import scrape_books
import os
from dotenv import load_dotenv

# Crear la instancia de Celery
load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
celery = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",  # Redis as broker
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"  # Save state
)

@celery.task
def scrape_books_task():
    try:
        scrape_books()
        return "Task Finished. Access to the books on /books"
    except:
        return "Error in the task"