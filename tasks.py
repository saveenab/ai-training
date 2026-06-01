# Saveena Boga - Celery Tasks

from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_classification(text: str) -> dict:
    # Simulate processing
    label = "positive" if len(text) > 10 else "negative"
    return {"text": text, "label": label}