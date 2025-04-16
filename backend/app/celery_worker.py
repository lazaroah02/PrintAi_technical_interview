from app.tasks import celery

# Ejecutar este archivo con:
# celery -A celery_worker.celery worker --loglevel=info