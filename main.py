from fastapi import FastAPI
from celery.result import AsyncResult
from tasks import add_task, celery_app

app = FastAPI()

@app.post("/add/")
def run_add(x: int, y: int):
    task = add_task.delay(x, y)
    return {"task_id": task.id}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
