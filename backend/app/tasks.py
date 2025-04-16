from celery import Celery
from app.scraping.scrape_books import scrape_books

# Crear la instancia de Celery
celery = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # Usando Redis como broker
    backend="redis://redis:6379/0"  # Para guardar estado
)

@celery.task
def scrape_books_task():
    try:
        scrape_books()
        return "Task Finished. Access to the books on /books"
    except:
        return "Error in the task"