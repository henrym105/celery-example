import os
from pathlib import Path
from time import sleep
import uuid

from celery import Celery

from inference import flip_rgb_to_bgr


# ----------------------------------------------------
# Define Celery app 
# ----------------------------------------------------
# Default result expiration time inside of redis and celery (seconds)
RESULT_EXPIRES = 5*60

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.update(
    result_expires=RESULT_EXPIRES,
    worker_concurrency=2,
    task_track_started=True,  # Enable progress tracking
)

# ----------------------------------------------------
# Define Tasks
# ----------------------------------------------------

@celery_app.task(bind=True)
def process_video_task(self, input_file_path: str):
    """Process video with progress updates"""
    try:
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Generate output path
        input_path = Path(input_file_path)
        output_filename = f"processed_{uuid.uuid4()}.mp4"
        output_path = Path("/app/output") / output_filename

        flip_rgb_to_bgr(input_file_path, output_path)


        return {
            "input_path": input_file_path,
            "output_path": str(output_path),
            "original_filename": input_path.name,
            "file_size": os.path.getsize(output_path),
            "status": "completed"
        }

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {
            "status": "failed",
            "error": str(e)
        }