import cv2
import numpy as np

def flip_rgb_to_bgr(input_path: str, output_path: str):
    """Flip RGB/BGR colors for video files"""
    cap = cv2.VideoCapture(input_path)
    
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
    return output_path
