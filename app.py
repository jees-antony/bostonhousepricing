from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import torch
from PIL import Image
import numpy as np
from io import BytesIO
from pathlib import Path

app = FastAPI()

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')


def detect_objects(image):
    # Perform object detection
    results = model(image)

    # Render bounding boxes on the image
    image_with_boxes = results.render()[0]

    # Convert numpy array to PIL Image
    image_with_boxes = Image.fromarray(image_with_boxes)

    return image_with_boxes

@app.post("/uploadfile/")
async def create_upload_file(file_image: UploadFile):
    return {"filename": file_image.filename}

@app.post("/detect")
async def detect_and_return_image(file: UploadFile = File(...)):
    
    # Read the uploaded image
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    # Detect objects in the uploaded image
    image_with_boxes = detect_objects(image)

    # Save the image with bounding boxes
    output_image_path = "image_with_boxes.jpg"
    image_with_boxes.save(output_image_path)

    # Return the image with bounding boxes
    return FileResponse(output_image_path)
