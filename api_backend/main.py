import os
from pathlib import Path
import uuid

import aiofiles
from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from tasks import process_video_task, celery_app

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR = Path("/app/output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/upload-and-process/")
async def upload_and_process_video(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    async with aiofiles.open(input_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Start processing task immediately
    task = process_video_task.delay(str(input_path))
    
    return {
        "task_id": task.id,
        "file_id": file_id,
        "original_filename": file.filename,
        "status": "processing"
    }

@app.get("/status/{task_id}")
def get_processing_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.status,
        "progress": None,
        "error": None
    }
    
    if result.ready():
        if result.successful():
            response["result"] = result.result
            response["download_ready"] = True
        else:
            response["error"] = str(result.info)
    else:
        # Check for progress updates if your task supports it
        if hasattr(result, 'info') and isinstance(result.info, dict):
            response["progress"] = result.info.get('progress', 0)
    
    return response

@app.get("/download/{task_id}")
def download_processed_video(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    
    if not result.ready():
        raise HTTPException(status_code=202, detail="Video still processing")
    
    if result.failed():
        raise HTTPException(status_code=500, detail="Processing failed")
    
    file_info = result.result
    output_path = file_info.get("output_path")
    
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Processed file not found")
    
    return FileResponse(
        output_path, 
        filename=f"processed_{file_info.get('original_filename', 'video.mp4')}",
        media_type='video/mp4'
    )