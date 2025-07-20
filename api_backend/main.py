import asyncio
import os
from pathlib import Path
import shutil
from time import time
import uuid

import aiofiles
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from tasks import celery_app, process_video_task

logger = get_task_logger(__name__)

UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR = Path("/app/output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

@app.post("/upload-and-process/")
async def upload_and_process_video(file: UploadFile = File(...)):
    """Upload video file and start processing task"""
    if not validate_video_file(file):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a video file (.mp4, .mov, .avi, .mkv)"
        )
    file_id = str(uuid.uuid4())
    input_path = save_uploaded_file(file, file_id)

    # Verify file exists and is readable before starting task
    if not os.path.exists(input_path):
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    # Additional verification - ensure file has content
    if os.stat(input_path).st_size == 0:
        raise HTTPException(status_code=500, detail="Uploaded file is empty")
    
    # Start processing task after confirming file is ready
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
            # Handle failed tasks properly
            response["error"] = str(result.info) if result.info else "Unknown error"
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Processing API. Use /upload-and-process/ to upload a video."}



# ------------------------------------------------------------
# Utility functions for file validation and saving
# ------------------------------------------------------------
def validate_video_file(file: UploadFile) -> bool:
    """Validate uploaded video file"""
    if not file.filename:
        return False
    
    allowed_extensions = {'.mp4', '.mov', '.avi', '.mkv'}
    file_ext = Path(file.filename).suffix.lower()
    
    return file_ext in allowed_extensions


def save_uploaded_file(file: UploadFile, file_id: str) -> str:
    """Save uploaded file to temporary directory"""
    file_ext = Path(file.filename).suffix.lower()
    temp_filename = f"{file_id}{file_ext}"
    temp_filepath = UPLOAD_DIR / temp_filename
    
    # Save file
    with open(temp_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"Saved uploaded file: {temp_filepath}")
    return str(temp_filepath)
