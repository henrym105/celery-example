from time import sleep
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def add_task(x, y):
    for i in range(x):
        sleep(1)
        print(f"Processing {i + 1}/{x}...")
    return x + y
