from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import shutil
import torch
from PIL import Image
import numpy as np
from io import BytesIO
import cv2

app = FastAPI()

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')


def detect_objects(image_path: str) -> np.ndarray:
    # Perform object detection
    results = model(image_path)

    # Render bounding boxes on the image
    image_with_boxes = results.render()[0]

    return image_with_boxes


@app.post("/detect")
async def detect_and_return_image(files: List[UploadFile] = File(...)):
    # Check if there's only one file uploaded
    if len(files) != 1:
        raise HTTPException(status_code=400, detail="Exactly one file should be uploaded.")

    # Save the uploaded image temporarily
    uploaded_file = files[0]
    with open(uploaded_file.filename, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    # Detect objects in the uploaded image
    image_with_boxes = detect_objects(uploaded_file.filename)

    # Convert numpy array to bytes
    image_bytes = cv2.imencode('.jpg', image_with_boxes)[1].tobytes()

    # Return the image with bounding boxes
    return FileResponse(BytesIO(image_bytes), media_type="image/jpeg")