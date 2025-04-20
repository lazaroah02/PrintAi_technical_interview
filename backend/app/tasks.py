import os

from celery import Celery
from dotenv import load_dotenv

from app.scraping.scrape_books import scrape_books

# Cargar variables de entorno
load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Crear la instancia de Celery
celery = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)


@celery.task
def scrape_books_task():
    try:
        scrape_books()
        return "Task Finished. Access to the books on /books"
    except Exception:
        return "Error in the task"
