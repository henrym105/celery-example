import os
import cv2
import numpy as np
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def flip_rgb_to_bgr(input_path: str, output_path: str):
    """Flip RGB/BGR colors for video files"""
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    # Check if file is accessible
    if not os.access(input_path, os.R_OK):
        logger.error(f"Input file is not readable: {input_path}")
        raise PermissionError(f"Input file is not readable: {input_path}")
    
    # Check if file has content
    if os.path.getsize(input_path) == 0:
        logger.error(f"Input file is empty: {input_path}")
        raise ValueError(f"Input file is empty: {input_path}")

    cap = cv2.VideoCapture(input_path)
    
    # Check if video file was opened successfully
    if not cap.isOpened():
        logger.error(f"Could not open video file: {input_path}")
        raise ValueError(f"Could not open video file: {input_path}")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame[:, :, [0, 2]] = frame[:, :, [2, 0]]  # Swap R and B channels
        out.write(frame)
    
    cap.release()
    out.release()

    if not os.path.exists(output_path):
        logger.error(f"Output file not found: {output_path}")
        raise RuntimeError(f"Failed to create output file: {output_path}")

    return output_path