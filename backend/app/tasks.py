from celery import Celery
from app.scraping.scrape_books import scrape_books

# Crear la instancia de Celery
celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Usando Redis como broker
    backend="redis://localhost:6379/0"  # Para guardar estado
)

@celery.task
def scrape_books_task():
    scrape_books()
    return "Scraping completo"
